"""High-Level User API for SymSentinel.

Provides `@symsentinel.monitor` and `symsentinel.wrap` to enable
drop-in, zero-overhead drift monitoring and cost-aware recalibration
for any quantum circuit.
"""

from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union
import numpy as np

from symsentinel.sentinels.base import BaseSentinel
from symsentinel.sentinels.parity import Z2ParitySentinel
from symsentinel.sentinels.magnetization import U1MagnetizationSentinel
from symsentinel.sentinels.spectator import SpectatorSentinel
from symsentinel.detect.edetector import EDetector
from symsentinel.certify.certificate import RiskCertificate
from symsentinel.control.cost_model import CostModel
from symsentinel.control.policy import ThreeTierController, RecalibrationAction


@dataclass
class SymSentinelConfig:
    """Configuration parameters for SymSentinel monitoring engine."""
    num_qubits: int = 8
    symmetry: str = "z2"  # 'z2', 'u1', or 'spectator'
    target_sector: int = 0  # 0 for even parity, k for U(1) weight
    spectator_indices: Sequence[int] = field(default_factory=lambda: [0])
    reference_mean: Optional[float] = None  # Baseline pre-change violation rate mu_0
    risk_target: float = 0.05
    alpha: float = 0.05
    cost_calibration: float = 100.0
    cost_uncertified: float = 20.0
    cost_per_shot: float = 0.0001
    cost_target: str = "80%_savings"
    min_validation_steps: int = 20


class SymSentinel:
    """The master SymSentinel runtime engine."""

    def __init__(self, config: Optional[SymSentinelConfig] = None, **kwargs):
        if config is None:
            self.config = SymSentinelConfig(**kwargs)
        else:
            self.config = config

        # 1. Instantiate the Sentinel
        if self.config.symmetry.lower() == "z2":
            self.sentinel: BaseSentinel = Z2ParitySentinel(
                num_qubits=self.config.num_qubits,
                target_parity=self.config.target_sector,
            )
        elif self.config.symmetry.lower() == "u1":
            self.sentinel = U1MagnetizationSentinel(
                num_qubits=self.config.num_qubits,
                target_weight=self.config.target_sector,
            )
        elif self.config.symmetry.lower() == "spectator":
            self.sentinel = SpectatorSentinel(
                num_qubits=self.config.num_qubits,
                spectator_indices=self.config.spectator_indices,
            )
        else:
            raise ValueError(f"Unknown symmetry '{self.config.symmetry}'. Choose 'z2', 'u1', or 'spectator'.")

        # 2. Cost Model
        self.cost_model = CostModel(
            cost_calibration=self.config.cost_calibration,
            cost_uncertified_epoch=self.config.cost_uncertified,
            cost_per_shot=self.config.cost_per_shot,
        )

        # 3. Initial Baseline & E-Detector
        self.baseline_violation: float = self.config.reference_mean if self.config.reference_mean is not None else 0.01
        gamma_star = self.cost_model.compute_optimal_gamma(delta_violation_shift=0.05)
        self.detector = EDetector(reference_mean=self.baseline_violation, threshold=gamma_star)

        # 4. Risk Certificate
        self.certifier = RiskCertificate(
            alpha=self.config.alpha,
            risk_target=self.config.risk_target,
        )

        # 5. 3-Tier Recalibration Controller
        self.controller = ThreeTierController(
            cost_model=self.cost_model,
            min_validation_steps=self.config.min_validation_steps,
        )
        self.epoch = 0

    def step(
        self,
        measurement_bitstrings: Sequence,
        validation_loss: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Process an epoch of measurement bitstrings.

        Returns:
            Diagnostic report with recommended RecalibrationAction, e-detector state,
            risk certificate, and cumulative cost savings.
        """
        self.epoch += 1
        num_shots = len(measurement_bitstrings)
        self.cost_model.record_shots(num_shots)

        # Compute empirical violation rate
        v_t = self.sentinel.violation_rate(measurement_bitstrings)
        delta_v = max(0.0, v_t - self.baseline_violation)

        # Update E-detector
        alarm_triggered = self.detector.step(v_t)

        # Update Risk Certificate
        if validation_loss is not None:
            self.certifier.update_validation(validation_loss)

        cert_val = self.certifier.compute_certificate(delta_v)
        is_cert = cert_val <= self.config.risk_target

        # Evaluate 3-tier Controller Action
        val_samples = len(self.certifier.cs.losses)
        action, reason = self.controller.evaluate_action(
            is_certified=is_cert,
            alarm_triggered=alarm_triggered,
            current_certificate=cert_val,
            target_tau=self.config.risk_target,
            validation_sample_count=val_samples,
        )

        # If full recalibration occurred, reset detector baseline
        if action == RecalibrationAction.TIER_3_FULL_RESET:
            self.baseline_violation = v_t
            self.detector.reset(new_reference_mean=v_t)
            self.certifier.reset_era()

        return {
            "epoch": self.epoch,
            "action": action.value,
            "reason": reason,
            "violation_rate": v_t,
            "edetector_stat": self.detector.stat,
            "edetector_alarm": alarm_triggered,
            "certificate": cert_val,
            "is_certified": is_cert,
            "cost_summary": self.cost_model.summary(),
        }


def monitor(
    risk_target: float = 0.05,
    symmetry: str = "z2",
    num_qubits: int = 8,
    cost_target: str = "80%_savings",
    **kwargs,
) -> Callable:
    """Decorator to monitor a quantum execution function with SymSentinel."""
    config = SymSentinelConfig(
        risk_target=risk_target,
        symmetry=symmetry,
        num_qubits=num_qubits,
        cost_target=cost_target,
        **kwargs,
    )
    engine = SymSentinel(config=config)

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kw) -> Tuple[Any, Dict[str, Any]]:
            result = fn(*args, **kw)
            if isinstance(result, tuple) and len(result) == 2 and hasattr(result[1], "__len__"):
                output, bitstrings = result
            elif hasattr(result, "__len__"):
                output, bitstrings = result, result
            else:
                return result, {"error": "Return value must be or include measurement bitstrings"}

            report = engine.step(bitstrings)
            return output, report

        wrapper.symsentinel = engine  # type: ignore
        return wrapper

    return decorator


def wrap(
    circuit_fn: Callable,
    risk_target: float = 0.05,
    symmetry: str = "z2",
    num_qubits: int = 8,
    **kwargs,
) -> Callable:
    """Functional wrapper equivalent to `@symsentinel.monitor`."""
    return monitor(
        risk_target=risk_target,
        symmetry=symmetry,
        num_qubits=num_qubits,
        **kwargs,
    )(circuit_fn)
