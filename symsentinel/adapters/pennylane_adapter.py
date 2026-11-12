"""PennyLane Framework Adapter for SymSentinel.

Integrates with PennyLane QNodes returning computational basis sample arrays,
enabling automatic symmetry extraction and anytime-valid drift control during
variational training (VQE / QNN / QAOA).
"""

from typing import Any, Callable, Dict, Optional, Sequence
import numpy as np

from symsentinel.api import SymSentinel, SymSentinelConfig


class PennyLaneSentinelAdapter:
    """Wraps PennyLane QNodes producing computational basis samples."""

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

    def monitor_samples(
        self,
        samples: np.ndarray,
        validation_loss: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Process PennyLane sample array of shape (shots, qubits)."""
        if not isinstance(samples, np.ndarray):
            samples = np.array(samples, dtype=np.int32)
        return self.engine.step(samples, validation_loss=validation_loss)

    def wrap_qnode(self, qnode_fn: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator for a PennyLane QNode returning samples."""
        def wrapped(*args, **kwargs):
            samples = qnode_fn(*args, **kwargs)
            report = self.monitor_samples(samples)
            return samples, report
        return wrapped
