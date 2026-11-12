"""Anytime-Valid Risk Certificate.

Combines the empirical-Bernstein validation confidence sequence with the
isotonic symmetry-drift link bound:
    U_t^cert = U_t^stat(alpha_stat) + U_t^link(alpha_link)
guaranteeing overall miscoverage rate at most alpha = alpha_stat + alpha_link.
"""

from typing import Optional
from symsentinel.certify.confidence_sequence import EmpiricalBernsteinCS
from symsentinel.certify.link_map import IsotonicRiskLink


class RiskCertificate:
    """Computes and tracks the combined anytime-valid risk certificate U_t^cert."""

    def __init__(
        self,
        alpha: float = 0.05,
        alpha_stat_ratio: float = 0.5,
        risk_target: float = 0.10,
        observable_norm: float = 1.0,
    ):
        self.alpha = float(alpha)
        self.alpha_stat = self.alpha * alpha_stat_ratio
        self.alpha_link = self.alpha * (1.0 - alpha_stat_ratio)
        self.risk_target = float(risk_target)

        self.cs = EmpiricalBernsteinCS(alpha=self.alpha_stat)
        self.link = IsotonicRiskLink(alpha_link=self.alpha_link, observable_norm=observable_norm)

    def update_validation(self, fresh_loss: float) -> float:
        """Incorporate fresh labeled validation loss and return current U_t^stat."""
        _, upper = self.cs.update(fresh_loss)
        return upper

    def compute_certificate(self, delta_violation: float) -> float:
        """Compute the combined certificate U_t^cert = U_t^stat + U_t^link."""
        u_stat = self.cs.get_upper_bound()
        u_link = self.link.predict_link_bound(delta_violation)
        cert = min(1.0, u_stat + u_link)
        return float(cert)

    def is_certified(self, delta_violation: float) -> bool:
        """Returns True if the certificate satisfies U_t^cert <= risk_target (tau)."""
        return self.compute_certificate(delta_violation) <= self.risk_target

    def reset_era(self) -> None:
        """Reset sequence for a new era after physical recalibration."""
        self.cs.reset()

