"""E-Detector for Sequential Change Detection with Guaranteed ARL Control.

Implements the Shiryaev-Roberts e-detector from Shin, Ramdas & Rinaldo (2022)
and Ramdas (2026). Guarantees Average Run Length inf_P E_P[T_gamma] >= gamma
and the optional-horizon inequality P(T_gamma <= sigma) <= E_P[sigma] / gamma.
"""

from typing import List, Optional, Sequence
import numpy as np


class EDetector:
    """Nonparametric e-detector on bounded symmetry violation stream z_t in [0, 1].

    Parameters:
        reference_mean: Pre-change baseline violation level mu_0.
        threshold: Alarm threshold gamma >= 10. Guaranteed ARL >= gamma.
        bet_grid: Optional grid of candidate betting parameters lambda_j > 0.
    """

    def __init__(
        self,
        reference_mean: float,
        threshold: float = 100.0,
        bet_grid: Optional[Sequence[float]] = None,
    ):
        if not (0.0 <= reference_mean < 1.0):
            raise ValueError(f"reference_mean must be in [0, 1), got {reference_mean}")
        if threshold < 1.0:
            raise ValueError(f"threshold gamma must be >= 1.0, got {threshold}")

        self.mu_0 = float(reference_mean)
        self.gamma = float(threshold)

        # Default mixture grid of positive bets for detecting increase in violation
        if bet_grid is None:
            # Range of bets tailored to sub-Gaussian variance proxy v = 1/4
            self.bet_grid = np.array([0.5, 1.0, 2.0, 3.5, 5.0], dtype=np.float64)
        else:
            self.bet_grid = np.array(bet_grid, dtype=np.float64)

        # Uniform mixture weights over bets
        self.weights = np.ones(len(self.bet_grid), dtype=np.float64) / len(self.bet_grid)

        self.stat: float = 0.0  # Shiryaev-Roberts statistic R_t, R_0 = 0
        self.history: List[float] = []
        self.stat_history: List[float] = [0.0]
        self.alarm_triggered: bool = False
        self.alarm_epoch: Optional[int] = None

    def compute_e_value(self, z: float) -> float:
        """Compute the mixture e-value for a single observation z:

            E(z) = sum_j w_j * exp(lambda_j * (z - mu_0) - lambda_j^2 / 8)
        """
        # Sub-Gaussian e-value with variance proxy 1/4 (because z in [0, 1])
        exponent = self.bet_grid * (z - self.mu_0) - (self.bet_grid ** 2) / 8.0
        # Numerical protection against overflow
        exponent = np.clip(exponent, -50.0, 50.0)
        e_vals = np.exp(exponent)
        return float(np.sum(self.weights * e_vals))

    def step(self, z: float) -> bool:
        """Process observation z_t, update Shiryaev-Roberts statistic R_t.

        Recursive Shiryaev-Roberts update:
            R_t = (1 + R_{t-1}) * E(z_t)

        Returns:
            True if alarm triggered (R_t >= gamma), False otherwise.
        """
        z_clamped = min(1.0, max(0.0, float(z)))
        e_val = self.compute_e_value(z_clamped)

        # Recursive update
        self.stat = (1.0 + self.stat) * e_val
        self.history.append(z_clamped)
        self.stat_history.append(self.stat)

        if self.stat >= self.gamma and not self.alarm_triggered:
            self.alarm_triggered = True
            self.alarm_epoch = len(self.history)
            return True

        return self.alarm_triggered

    def reset(self, new_reference_mean: Optional[float] = None) -> None:
        """Reset the detector for a new calibration era."""
        if new_reference_mean is not None:
            self.mu_0 = float(new_reference_mean)
        self.stat = 0.0
        self.history.clear()
        self.stat_history = [0.0]
        self.alarm_triggered = False
        self.alarm_epoch = None

