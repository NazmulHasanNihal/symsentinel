"""3-Tier Recalibration Controller & Three-Rule Stopping Policy.

Implements the multi-tiered cost-aware recalibration policy:
  - Check 1: Certify & Stop (if U_t^cert <= tau)
  - Check 2: Budget Check (Abstain if remaining budget < c_cal + c_val)
  - Check 3: Alarm Check -> 3-Tier Recalibration Cascade:
      * Tier 1: Virtual-Z frame shift (Software fix, 0 cost)
      * Tier 2: Localized subsystem recalibration (0.15 * c_cal)
      * Tier 3: Full hardware recalibration (1.0 * c_cal)
"""

from enum import Enum
from typing import Dict, Optional, Tuple
from symsentinel.control.cost_model import CostModel


class RecalibrationAction(Enum):
    CONTINUE = "CONTINUE"
    CERTIFY_AND_STOP = "CERTIFY_AND_STOP"
    ABSTAIN = "ABSTAIN"
    TIER_1_SOFTWARE_FIX = "TIER_1_SOFTWARE_FIX"
    TIER_2_SUBSYSTEM = "TIER_2_SUBSYSTEM"
    TIER_3_FULL_RESET = "TIER_3_FULL_RESET"


class ThreeTierController:
    """Orchestrates runtime recalibration decisions to maximize cost savings."""

    def __init__(
        self,
        cost_model: CostModel,
        budget_limit: float = 1000.0,
        min_validation_steps: int = 20,
        consecutive_alarm_limit: int = 2,
    ):
        self.cost_model = cost_model
        self.budget_limit = float(budget_limit)
        self.min_validation_steps = int(min_validation_steps)
        self.consecutive_alarm_limit = int(consecutive_alarm_limit)

        self.consecutive_alarms: int = 0
        self.current_era: int = 0

    def evaluate_action(
        self,
        is_certified: bool,
        alarm_triggered: bool,
        current_certificate: float,
        target_tau: float,
        validation_sample_count: int = 0,
        remaining_budget: Optional[float] = None,
    ) -> Tuple[RecalibrationAction, str]:
        """Decide next action in order of the 3-rule procedure.

        Returns:
            (action, reason_explanation)
        """
        # Rule 1: Certify and stop
        if is_certified and current_certificate <= target_tau:
            return RecalibrationAction.CERTIFY_AND_STOP, f"Risk certificate {current_certificate:.4f} <= {target_tau:.4f} achieved."

        # Rule 2: Budget check
        rem = self.budget_limit - self.cost_model.total_cost() if remaining_budget is None else remaining_budget
        min_required_reserve = self.cost_model.c_cal + 20.0
        if rem < min_required_reserve:
            return RecalibrationAction.ABSTAIN, f"Remaining budget {rem:.2f} insufficient for calibration and validation."

        # Rule 3: Alarm check
        # Only check certificate exceedance after validation stream has accumulated min samples
        val_stream_grown = (validation_sample_count >= self.min_validation_steps)
        cert_exceeded = val_stream_grown and (current_certificate > target_tau * 1.5)

        if not alarm_triggered and not cert_exceeded:
            self.consecutive_alarms = 0
            return RecalibrationAction.CONTINUE, "Detector healthy, proceeding to next epoch."

        # Alarm triggered or mature certificate exceeded tolerance
        self.consecutive_alarms += 1

        if self.consecutive_alarms == 1:
            # First alarm: try Tier 1 Virtual-Z / software compensation
            self.cost_model.record_calibration(tier_discount=0.0)
            return RecalibrationAction.TIER_1_SOFTWARE_FIX, "Tier 1: Applying zero-cost virtual-Z phase frame shift."

        elif self.consecutive_alarms == 2:
            # Second persistent alarm: localized subsystem recalibration
            self.cost_model.record_calibration(tier_discount=0.15)
            self.current_era += 1
            return RecalibrationAction.TIER_2_SUBSYSTEM, "Tier 2: Recalibrating localized subsystem coupler/qubit."

        else:
            # Severe drift: full hardware reset
            self.cost_model.record_calibration(tier_discount=1.0)
            self.current_era += 1
            self.consecutive_alarms = 0
            return RecalibrationAction.TIER_3_FULL_RESET, "Tier 3: Triggering full QPU hardware recalibration."
