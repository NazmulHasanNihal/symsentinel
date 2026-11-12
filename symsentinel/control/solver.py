"""Renewal-reward optimal stopping threshold solver."""
import numpy as np


def solve_optimal_gamma(
    cost_calibration: float = 100.0,
    cost_risk_penalty: float = 20.0,
    nu_0: float = 0.05,
    delta_violation: float = 0.04,
    gamma_min: float = 10.0,
) -> float:
    r"""Calculates first-order renewal-reward cost-optimal stopping threshold:

        \gamma^* = \max\left(\gamma_{\min}, \frac{c_{\mathrm{cal}} \cdot D_{\mathrm{KL}}(\nu_1 \parallel \nu_0)}{c_{\mathrm{risk}} \cdot \Delta R}\right)
    """
    nu_1 = min(0.99, max(0.01, nu_0 + delta_violation))
    nu_0_clamped = min(0.99, max(0.01, nu_0))
    dkl = nu_1 * np.log(nu_1 / nu_0_clamped) + (1.0 - nu_1) * np.log((1.0 - nu_1) / (1.0 - nu_0_clamped))
    delta_R = max(0.01, delta_violation * 1.5)
    gamma_star = (cost_calibration * dkl) / (max(cost_risk_penalty, 1e-4) * delta_R)
    return float(max(gamma_min, gamma_star))

