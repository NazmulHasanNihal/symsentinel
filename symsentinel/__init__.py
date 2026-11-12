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
from symsentinel.control.policy import ThreeTierController, RecalibrationAction

__version__ = "0.1.0"
__all__ = [
    "monitor",
    "wrap",
    "SymSentinelConfig",
    "BaseSentinel",
    "Z2ParitySentinel",
    "U1MagnetizationSentinel",
    "SpectatorSentinel",
    "EDetector",
    "BettingMartingale",
    "RiskCertificate",
    "ThreeTierController",
    "RecalibrationAction",
]
