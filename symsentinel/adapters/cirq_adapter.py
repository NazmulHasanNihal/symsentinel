"""Cirq Framework Adapter for SymSentinel.

Integrates with Google Cirq Samplers and TrialResults, extracting free
symmetry syndromes from measurement bitstrings for real-time drift monitoring.
"""

from typing import Any, Callable, Dict, Optional
import numpy as np

from symsentinel.api import SymSentinel, SymSentinelConfig


class CirqSentinelAdapter:
    """Wraps Cirq execution and extracts syndromes from cirq.Result measurements."""

    def __init__(
        self,
        num_qubits: int,
        symmetry: str = "z2",
        target_sector: int = 0,
        risk_target: float = 0.08,
        alpha: float = 0.05,
    ):
        self.config = SymSentinelConfig(
            num_qubits=num_qubits,
            symmetry=symmetry,
            target_sector=target_sector,
            risk_target=risk_target,
            alpha=alpha,
        )
        self.engine = SymSentinel(config=self.config)

    def monitor_trial_result(
        self,
        result: Any,
        measurement_key: Optional[str] = None,
        validation_loss: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Extract measurement array from a Cirq Result object."""
        if hasattr(result, "measurements"):
            if measurement_key is not None and measurement_key in result.measurements:
                bits = result.measurements[measurement_key]
            else:
                # Take the first available key
                first_key = next(iter(result.measurements.keys()))
                bits = result.measurements[first_key]
        elif isinstance(result, np.ndarray):
            bits = result
        else:
            raise TypeError(f"Expected Cirq Result with measurements attribute, got {type(result)}")

        return self.engine.step(bits, validation_loss=validation_loss)
