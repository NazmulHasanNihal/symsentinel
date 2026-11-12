"""Qiskit Framework Adapter for SymSentinel.

Provides zero-boilerplate integration with IBM Qiskit QPU and Simulator backends,
automatically intercepting measurement bitstrings, computing primary expectation
values, and extracting free symmetry syndromes with anytime-valid drift detection.
"""

from typing import Any, Callable, Dict, List, Optional, Sequence, Union
import numpy as np

from symsentinel.api import SymSentinel, SymSentinelConfig


class QiskitSentinelAdapter:
    """Wraps Qiskit backend execution with in-situ SymSentinel monitoring."""

    def __init__(
        self,
        config: Optional[SymSentinelConfig] = None,
        num_qubits: int = 6,
        symmetry: str = "z2",
        target_sector: int = 0,
        risk_target: float = 0.08,
        alpha: float = 0.05,
    ):
        if config is None:
            self.config = SymSentinelConfig(
                num_qubits=num_qubits,
                symmetry=symmetry,
                target_sector=target_sector,
                risk_target=risk_target,
                alpha=alpha,
            )
        else:
            self.config = config

        self.engine = SymSentinel(config=self.config)

    def parse_qiskit_counts(self, counts: Dict[str, int]) -> List[str]:
        """Convert Qiskit counts dictionary (e.g. {'000000': 500, '000001': 524})
        into an expanded list of individual measurement bitstrings.
        """
        expanded = []
        for bitstring, count in counts.items():
            # Qiskit bitstrings may have spaces between classical registers; strip them
            clean_str = bitstring.replace(" ", "")
            expanded.extend([clean_str] * count)
        return expanded

    def monitor_counts(
        self,
        counts: Dict[str, int],
        validation_loss: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Feed a Qiskit Result counts dictionary to the SymSentinel engine.

        Returns:
            Diagnostic report containing recalibration action, e-detector state,
            and anytime risk certificate.
        """
        bitstrings = self.parse_qiskit_counts(counts)
        return self.engine.step(bitstrings, validation_loss=validation_loss)

    def wrap_execute(self, execute_fn: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator wrapping a Qiskit execution callable."""
        def wrapped(*args, **kwargs):
            result = execute_fn(*args, **kwargs)
            # Try extracting counts
            if hasattr(result, "get_counts"):
                counts = result.get_counts()
                report = self.monitor_counts(counts)
                return result, report
            elif isinstance(result, dict):
                report = self.monitor_counts(result)
                return result, report
            return result
        return wrapped
