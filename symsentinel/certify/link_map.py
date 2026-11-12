"""Isotonic Regression Link Map from Symmetry Violation to Risk Shift.

Implements Section 4.4 of the research plan: bounding task risk degradation
Delta_t <= h(nu_t - nu_0) + kappa_t using an isotonic nondecreasing estimator h
with confidence sequence residual margins kappa_t.
"""

from typing import List, Tuple
import numpy as np


def pool_adjacent_violators(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Pure NumPy implementation of the Pool Adjacent Violators Algorithm (PAVA)
    for 1D nondecreasing isotonic regression.
    """
    order = np.argsort(x)
    x_sorted = x[order]
    y_sorted = y[order]

    # Blocks: list of [weight, sum_y, mean_y, min_x, max_x]
    blocks = [[1.0, float(y_val), float(y_val), float(x_val), float(x_val)] for x_val, y_val in zip(x_sorted, y_sorted)]

    i = 0
    while i < len(blocks) - 1:
        if blocks[i][2] > blocks[i + 1][2]:
            # Violation of monotonicity: merge blocks i and i+1
            w1, s1, _, min_x1, _ = blocks[i]
            w2, s2, _, _, max_x2 = blocks[i + 1]
            new_w = w1 + w2
            new_s = s1 + s2
            new_m = new_s / new_w
            blocks[i] = [new_w, new_s, new_m, min_x1, max_x2]
            del blocks[i + 1]
            if i > 0:
                i -= 1
        else:
            i += 1

    fitted_x = np.array([b[4] for b in blocks])
    fitted_y = np.array([b[2] for b in blocks])
    return fitted_x, fitted_y


class IsotonicRiskLink:
    """Estimates and evaluates the monotonic upper link h(Delta nu) + kappa_t."""

    def __init__(self, alpha_link: float = 0.025, observable_norm: float = 1.0):
        self.alpha_link = float(alpha_link)
        self.norm_O = float(observable_norm)

        self.probe_violations: List[float] = []
        self.probe_risk_shifts: List[float] = []
        self.fitted_x: Optional[np.ndarray] = None
        self.fitted_y: Optional[np.ndarray] = None
        self.residual_margin: float = 0.05

    def add_probe(self, delta_violation: float, measured_risk_shift: float) -> None:
        """Add a calibration probe pair from noise amplification or validation."""
        self.probe_violations.append(max(0.0, float(delta_violation)))
        self.probe_risk_shifts.append(float(measured_risk_shift))

    def fit(self) -> None:
        """Fit the isotonic nondecreasing link curve and compute residual margin kappa_t."""
        if len(self.probe_violations) < 2:
            # Not enough probes: fall back to conservative analytical bound
            self.fitted_x = np.array([0.0, 1.0])
            self.fitted_y = np.array([0.0, 2.0 * self.norm_O])
            self.residual_margin = 0.05
            return

        x_arr = np.array(self.probe_violations, dtype=np.float64)
        y_arr = np.array(self.probe_risk_shifts, dtype=np.float64)

        # Force monotonicity via PAVA
        self.fitted_x, self.fitted_y = pool_adjacent_violators(x_arr, y_arr)

        # Compute residuals and statistical margin
        pred = np.interp(x_arr, self.fitted_x, self.fitted_y)
        res = y_arr - pred
        n = len(res)
        res_var = float(np.var(res))
        # Confidence margin kappa_t
        self.residual_margin = float(np.sqrt(2.0 * (res_var + 1e-4) * np.log(2.0 / self.alpha_link) / n) + 0.01)

    def predict_link_bound(self, delta_violation: float) -> float:
        """Evaluate U_t^link = h_hat(Delta nu) + kappa_t."""
        dv = max(0.0, float(delta_violation))
        if self.fitted_x is None:
            self.fit()

        assert self.fitted_x is not None and self.fitted_y is not None
        h_val = float(np.interp(dv, self.fitted_x, self.fitted_y))
        # Exact physical leakage bound: |Delta R| <= 2 * Delta p * ||O||_inf
        physical_cap = 2.0 * dv * self.norm_O
        return min(h_val + self.residual_margin, physical_cap + self.residual_margin)

