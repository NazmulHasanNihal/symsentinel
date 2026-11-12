"""Unit Tests for SymSentinel Framework Adapters and CLI."""

import numpy as np
import pytest
from symsentinel.adapters.qiskit_adapter import QiskitSentinelAdapter
from symsentinel.adapters.pennylane_adapter import PennyLaneSentinelAdapter
from symsentinel.adapters.cirq_adapter import CirqSentinelAdapter
from symsentinel.cli import main


def test_qiskit_adapter():
    adapter = QiskitSentinelAdapter(num_qubits=4, symmetry="z2")
    counts = {"0000": 800, "0011": 200, "0001": 24}
    report = adapter.monitor_counts(counts)
    assert "action" in report
    assert "edetector_stat" in report
    assert report["action"] == "CONTINUE"


def test_pennylane_adapter():
    adapter = PennyLaneSentinelAdapter(num_qubits=4, symmetry="z2")
    # Even parity samples
    samples = np.array([
        [0, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0],
    ])
    report = adapter.monitor_samples(samples)
    assert report["violation_rate"] == 0.0
    assert report["action"] == "CONTINUE"


def test_cirq_adapter():
    adapter = CirqSentinelAdapter(num_qubits=4, symmetry="z2")
    measurements = np.array([
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 1, 1],
    ])
    class MockCirqResult:
        def __init__(self, m):
            self.measurements = {"m": m}

    res = MockCirqResult(measurements)
    report = adapter.monitor_trial_result(res)
    assert report["violation_rate"] == 0.0
    assert report["action"] == "CONTINUE"
