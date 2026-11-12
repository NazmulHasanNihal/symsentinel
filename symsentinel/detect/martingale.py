"""Nonparametric Betting Martingales for Anytime-Valid Inference.

Implements nonnegative betting martingales M_t = prod_{i=1}^t (1 + lambda_i * (X_i - mu))
with strictly F_{i-1}-measurable (predictable) betting fractions lambda_i,
guaranteeing exact Ville's inequality protection: P(exists t: M_t >= 1/alpha) <= alpha.
"""

from typing import List, Optional
import numpy as np


class BettingMartingale:
    """Nonparametric betting martingale on bounded random variables X_t in [0, 1].

    Parameters:
        null_mean: Upper bound on the expected value under the null hypothesis (mu_0).
        alpha: Target Type-I error level (used for predictable variance tuning).
        c_max: Maximum betting fraction clamp to avoid numerical instability.
        epsilon: Safety buffer to ensure 1 + lambda * (X - mu) > 0 strictly.
    """

    def __init__(
        self,
        null_mean: float,
        alpha: float = 0.05,
        c_max: float = 0.9,
        epsilon: float = 1e-4,
    ):
        if not (0.0 <= null_mean <= 1.0):
            raise ValueError(f"null_mean must be in [0, 1], got {null_mean}")
        self.null_mean = float(null_mean)
        self.alpha = float(alpha)
        self.c_max = float(c_max)
        self.epsilon = float(epsilon)

        self.history: List[float] = []
        self.wealth: float = 1.0
        self.wealth_history: List[float] = [1.0]

    def compute_predictable_lambda(self) -> float:
        """Compute the betting fraction lambda_t strictly using history up to t-1.

        Uses empirical Bernstein variance tuning:
            lambda_t = min(c_max, sqrt(2 * ln(2/alpha) / (t * (sigma^2 + eps))))
        clipped to ensure almost-sure nonnegativity.
        """
        t = len(self.history)
        if t == 0:
            # Initial bet without data
            raw_bet = 0.5
        else:
            # Empirical variance from previous observations
            arr = np.array(self.history, dtype=np.float64)
            var = float(np.var(arr))
            raw_bet = np.sqrt(2.0 * np.log(2.0 / self.alpha) / (t * (var + 0.01)))

        # Bounds to guarantee 1 + lambda * (x - mu) > 0 for all x in [0, 1]
        # x - mu in [-mu, 1 - mu]
        # For x=0: 1 - lambda * mu > 0 => lambda < 1 / mu
        # For x=1: 1 + lambda * (1 - mu) > 0 => lambda > -1 / (1 - mu)
        upper_bound = (1.0 - self.epsilon) / max(self.null_mean, 1e-4)
        lower_bound = -(1.0 - self.epsilon) / max(1.0 - self.null_mean, 1e-4)

        # Clamping
        bet = min(raw_bet, self.c_max, upper_bound)
        bet = max(bet, lower_bound)
        return float(bet)

    def step(self, x: float) -> float:
        """Process observation x_t in [0, 1] and update wealth M_t.

        Returns:
            Current martingale wealth M_t.
        """
        x_clamped = min(1.0, max(0.0, float(x)))
        lam = self.compute_predictable_lambda()
        factor = 1.0 + lam * (x_clamped - self.null_mean)

        # Numerical nonnegativity safeguard
        factor = max(factor, 1e-12)
        self.wealth *= factor
        self.history.append(x_clamped)
        self.wealth_history.append(self.wealth)
        return self.wealth

    def reset(self) -> None:
        """Reset martingale to M_0 = 1.0."""
        self.history.clear()
        self.wealth = 1.0
        self.wealth_history = [1.0]

