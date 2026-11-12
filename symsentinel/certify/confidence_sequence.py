"""Empirical-Bernstein Anytime-Valid Confidence Sequences for Risk Certification.

Implements time-uniform non-asymptotic confidence sequences (Howard et al., 2021;
Waudby-Smith & Ramdas, 2024) bounding population risk at all stopping times with
guaranteed failure probability at most alpha_stat.
"""

from typing import List, Tuple
import numpy as np


class EmpiricalBernsteinCS:
    """Time-uniform empirical-Bernstein confidence sequence for bounded losses L in [0, 1].

    Parameters:
        alpha: Target miscoverage rate (e.g. 0.025 for 97.5% coverage).
        c_scale: Tuning parameter for variance proxy.
    """

    def __init__(self, alpha: float = 0.025, c_scale: float = 0.5):
        if not (0.0 < alpha < 1.0):
            raise ValueError(f"alpha must be in (0, 1), got {alpha}")
        self.alpha = float(alpha)
        self.c_scale = float(c_scale)

        self.losses: List[float] = []
        self.running_sum: float = 0.0
        self.running_sq_sum: float = 0.0
        self.current_lower: float = 0.0
        self.current_upper: float = 1.0

    def update(self, loss: float) -> Tuple[float, float]:
        """Incorporate a new fresh validation loss observation L_t in [0, 1].

        Returns:
            (lower_bound, upper_bound) valid at the current time step t.
        """
        l_clamped = min(1.0, max(0.0, float(loss)))
        self.losses.append(l_clamped)
        t = len(self.losses)

        self.running_sum += l_clamped
        self.running_sq_sum += l_clamped ** 2

        mean = self.running_sum / t
        var = max(0.0, (self.running_sq_sum / t) - (mean ** 2))

        # Time-uniform stitching boundary for empirical Bernstein
        # Howard et al. (2021) / Waudby-Smith & Ramdas (2024)
        log_term = np.log(2.0 / self.alpha) + np.log(np.log(max(np.e, float(t))) + 1.0)
        radius = np.sqrt(2.0 * (var + 1e-4) * log_term / t) + (3.0 * log_term / t)

        self.current_lower = float(max(0.0, mean - radius))
        self.current_upper = float(min(1.0, mean + radius))
        return self.current_lower, self.current_upper

    def get_upper_bound(self) -> float:
        """Returns the current risk upper bound U_t^stat."""
        return self.current_upper

    def reset(self) -> None:
        """Reset sequence for a new era."""
        self.losses.clear()
        self.running_sum = 0.0
        self.running_sq_sum = 0.0
        self.current_lower = 0.0
        self.current_upper = 1.0
