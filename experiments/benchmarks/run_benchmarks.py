"""Standalone Benchmark Suite Runner for SymSentinel Circuits B1-B3 & Regimes D1-D4."""

import os
import sys
import numpy as np

# Ensure root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from symsentinel.sim import BenchmarkHarness, BenchmarkCircuits
from symsentinel.api import SymSentinel, SymSentinelConfig


def run_benchmark_suite(epochs: int = 50, shots: int = 1024):
    print("=" * 75)
    print(" RUNNING SYMSENTINEL BENCHMARKS B1 (TFIM Z2) & B2 (XXZ U1) UNDER D1-D4")
    print("=" * 75)

    harness = BenchmarkHarness(num_qubits=8, seed=42)
    benchmarks = ["B1", "B2"]
    regimes = ["D1", "D2", "D3", "D4"]

    for b in benchmarks:
        for r in regimes:
            config = SymSentinelConfig(num_qubits=8, symmetry="z2" if b == "B1" else "u1")
            engine = SymSentinel(config=config)
            actions = []
            for ep in range(1, epochs + 1):
                bits, nu = harness.run_epoch(benchmark=b, regime=r, epoch=ep, num_shots=shots)
                report = engine.step(bits)
                actions.append(report["action"])

            recal_count = sum(1 for a in actions if "RECAL" in a or "TIER" in a)
            print(f"Benchmark {b} | Regime {r} | Total Epochs: {epochs} | Calibrations: {recal_count} | Final Action: {actions[-1]}")

    print("\nBenchmark Suite completed successfully!")


if __name__ == "__main__":
    run_benchmark_suite(epochs=20, shots=512)
