"""Sentinel Library & Greedy Set-Cover Selector for Blind-Spot Mitigation.

Implements Theorem T2: selecting the minimal-cost subset of symmetry sentinels
to cover all candidate fault families (e.g., X, Y, Z Pauli faults across qubits).
"""

from typing import Dict, List, Sequence, Set
import numpy as np
from symsentinel.sentinels.base import BaseSentinel


class SentinelLibrary:
    """Manages a collection of candidate sentinels and selects optimal subsets."""

    def __init__(self):
        self.sentinels: List[BaseSentinel] = []
        self.costs: List[float] = []
        # Maps sentinel index -> set of detectable fault IDs
        self.coverage_map: Dict[int, Set[str]] = {}

    def register_sentinel(
        self,
        sentinel: BaseSentinel,
        detectable_faults: Sequence[str],
        measurement_cost: float = 0.0,
    ) -> int:
        """Register a candidate sentinel.

        Parameters:
            sentinel: BaseSentinel instance.
            detectable_faults: List of fault identifiers (e.g. ['X_0', 'Y_1', 'Z_2'])
                               that anticommute with this sentinel's operator.
            measurement_cost: Shot/basis cost of measuring this sentinel (0 if free).

        Returns:
            Index of the registered sentinel.
        """
        idx = len(self.sentinels)
        self.sentinels.append(sentinel)
        self.costs.append(max(0.01, float(measurement_cost)))  # small epsilon for zero-cost
        self.coverage_map[idx] = set(detectable_faults)
        return idx

    def greedy_set_cover(self, target_faults: Sequence[str]) -> List[int]:
        """Greedy set-cover algorithm achieving (1 + ln m) approximation to minimum cost.

        Parameters:
            target_faults: All fault types that must be visible to the monitor.

        Returns:
            List of sentinel indices achieving the cover.
        """
        uncovered: Set[str] = set(target_faults)
        selected_indices: List[int] = []

        while uncovered:
            best_idx = None
            best_ratio = float("inf")

            for idx, sentinel in enumerate(self.sentinels):
                newly_covered = len(self.coverage_map[idx] & uncovered)
                if newly_covered > 0:
                    cost = self.costs[idx]
                    ratio = cost / newly_covered
                    if ratio < best_ratio:
                        best_ratio = ratio
                        best_idx = idx

            if best_idx is None:
                # Some faults cannot be covered by the library
                break

            selected_indices.append(best_idx)
            uncovered -= self.coverage_map[best_idx]

        return selected_indices

    def evaluate_library_stream(
        self,
        bitstrings: Sequence,
        selected_indices: Sequence[int],
    ) -> float:
        """Aggregate violation across selected sentinels (union of alarms)."""
        if not selected_indices:
            return 0.0
        # If any selected sentinel detects violation in a shot, shot is violated
        total_shots = len(bitstrings)
        if total_shots == 0:
            return 0.0

        violated_shots = np.zeros(total_shots, dtype=bool)
        for s_idx in selected_indices:
            sentinel = self.sentinels[s_idx]
            batch_v = sentinel.evaluate_batch(bitstrings)
            violated_shots |= (batch_v > 0)

        return float(np.mean(violated_shots))

