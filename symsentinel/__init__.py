"""SymSentinel: Anytime-Valid Recalibration of Symmetric Quantum Learners under Hardware Drift.

An open-source library for monitoring quantum hardware drift at zero extra shot cost,
guaranteeing anytime-valid false-alarm control (ARL) and certified risk bounds.
"""

from symsentinel.api import monitor, wrap, SymSentinel, SymSentinelConfig
from symsentinel.sentinels.base import BaseSentinel
from symsentinel.sentinels.parity import Z2ParitySentinel
from symsentinel.sentinels.magnetization import U1MagnetizationSentinel
from symsentinel.sentinels.spectator import SpectatorSentinel
from symsentinel.detect.edetector import EDetector
from symsentinel.detect.martingale import BettingMartingale
from symsentinel.certify.certificate import RiskCertificate
from symsentinel.certify import TwoLayerRiskBridge
from symsentinel.control.policy import ThreeTierController, RecalibrationAction
from symsentinel.control import CostModel, solve_optimal_gamma
from symsentinel.symmetry import (
    z2_parity_violation_rate,
    u1_charge_leakage_rate,
    invert_gate_error_from_violation,
    zero_depth_spam_probe,
)
from symsentinel.sim import (
    BenchmarkCircuits,
    DriftSimulator,
    MultiDayIBMCalibrationReplay,
    BenchmarkHarness,
)

__version__ = "0.1.0"
__all__ = [
    "monitor",
    "wrap",
    "SymSentinel",
    "SymSentinelConfig",
    "BaseSentinel",
    "Z2ParitySentinel",
    "U1MagnetizationSentinel",
    "SpectatorSentinel",
    "EDetector",
    "BettingMartingale",
    "RiskCertificate",
    "TwoLayerRiskBridge",
    "ThreeTierController",
    "RecalibrationAction",
    "CostModel",
    "solve_optimal_gamma",
    "z2_parity_violation_rate",
    "u1_charge_leakage_rate",
    "invert_gate_error_from_violation",
    "zero_depth_spam_probe",
    "BenchmarkCircuits",
    "DriftSimulator",
    "MultiDayIBMCalibrationReplay",
    "BenchmarkHarness",
]
