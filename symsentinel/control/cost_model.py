"""Cost Model & Optimal E-Detector Threshold Calculator.

Implements Section 4.6: computing the cost-optimal e-detector threshold gamma*
that minimizes expected operational loss J(gamma) = c_cal / gamma + c_d * ln(gamma) / (2 * delta^2).
"""

from typing import Dict
import numpy as np


class CostModel:
    """Calculates optimal threshold gamma* and tracks total economic expenditure.

    Parameters:
        cost_calibration: Cost of full hardware recalibration c_cal (e.g. $100 or credits).
        cost_uncertified_epoch: Cost penalty per epoch of running uncertified c_d.
        cost_per_shot: Marginal fee per quantum measurement shot (e.g. $0.0001).
        min_threshold_floor: Lower bound for gamma (default 10.0).
    """

    def __init__(
        self,
        cost_calibration: float = 100.0,
        cost_uncertified_epoch: float = 20.0,
        cost_per_shot: float = 0.0001,
        min_threshold_floor: float = 10.0,
    ):
        self.c_cal = float(cost_calibration)
        self.c_d = float(cost_uncertified_epoch)
        self.c_shot = float(cost_per_shot)
        self.gamma_min = float(min_threshold_floor)

        # Cumulative expenditures
        self.total_calibration_cost: float = 0.0
        self.total_shot_cost: float = 0.0
        self.total_shots: int = 0
        self.calibration_count: int = 0

    def compute_optimal_gamma(self, delta_violation_shift: float) -> float:
        """First-order cost-optimal threshold:

            gamma* = max(gamma_min, (2 * delta^2 * c_cal) / c_d)
        """
        d = max(0.01, float(delta_violation_shift))
        gamma_star = (2.0 * (d ** 2) * self.c_cal) / max(self.c_d, 1e-4)
        return float(max(self.gamma_min, gamma_star))

    def record_shots(self, count: int) -> None:
        """Record quantum shots used."""
        self.total_shots += count
        self.total_shot_cost += count * self.c_shot

    def record_calibration(self, tier_discount: float = 1.0) -> float:
        """Record calibration fee (tier_discount = 0.0 for software, 0.15 for subsystem, 1.0 for full)."""
        fee = self.c_cal * tier_discount
        self.total_calibration_cost += fee
        self.calibration_count += 1
        return fee

    def total_cost(self) -> float:
        """Returns total dollar / credit expenditure so far."""
        return self.total_calibration_cost + self.total_shot_cost

    def summary(self) -> Dict[str, float]:
        return {
            "total_cost": self.total_cost(),
            "calibration_cost": self.total_calibration_cost,
            "shot_cost": self.total_shot_cost,
            "calibrations": float(self.calibration_count),
            "shots": float(self.total_shots),
        }

