"""SymSentinel Quickstart: Real-World Demonstration.

Demonstrates how to use SymSentinel on a quantum learner under hardware drift,
achieving real-time drift detection, certified risk tracking, and 80%+ cost savings.
"""

import os
import sys
import time
import numpy as np

# Ensure root directory is on sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import symsentinel as ss
from symsentinel.sim.drift import DriftSimulator


def main():
    print("=" * 75)
    print("   SymSentinel: Real-Time Quantum Hardware Drift Monitor & Recalibration")
    print("=" * 75)

    num_qubits = 6
    num_epochs = 20
    shots_per_epoch = 1024

    # Initialize physical drift simulator with sudden jump at epoch 12
    sim = DriftSimulator(num_qubits=num_qubits, target_parity=0, seed=42)

    # 1. Cold start baseline estimation (Epoch 0)
    print("\n[Phase 1] Cold Start: Measuring nominal hardware baseline...")
    cold_bits, _ = sim.sample_d1_coherent(epoch=0, num_shots=shots_per_epoch)
    sentinel = ss.Z2ParitySentinel(num_qubits=num_qubits, target_parity=0)
    baseline_v = sentinel.violation_rate(cold_bits)
    print(f" -> Nominal Baseline Violation Rate: mu_0 = {baseline_v:.4f}")

    # 2. Configure SymSentinel
    config = ss.SymSentinelConfig(
        num_qubits=num_qubits,
        symmetry="z2",
        reference_mean=baseline_v,
        risk_target=0.08,
        cost_calibration=100.0,
        cost_per_shot=0.0001,
        min_validation_steps=5,
    )
    engine = ss.SymSentinel(config=config)

    print("\n[Phase 2] Running Workload across 20 Epochs with Injected Drift at Epoch 12...")
    print("-" * 75)
    print(f"{'Epoch':<6} | {'Violation':<10} | {'E-Detector R_t':<15} | {'Certificate':<12} | {'Action Recommended'}")
    print("-" * 75)

    for epoch in range(1, num_epochs + 1):
        # Inject physical TLS jump drift starting at epoch 12
        if epoch < 12:
            bits, _ = sim.sample_d1_coherent(epoch=epoch, num_shots=shots_per_epoch)
            loss = 0.03 + np.random.normal(0, 0.005)
        else:
            # Physical hardware fault occurs
            bits, _, _ = sim.sample_d3_jump(epoch=epoch, jump_epoch=12, num_shots=shots_per_epoch, jump_magnitude=0.15)
            loss = 0.12 + np.random.normal(0, 0.01)

        report = engine.step(bits, validation_loss=loss)

        v_str = f"{report['violation_rate']:.4f}"
        stat_str = f"{report['edetector_stat']:.3f}"
        cert_str = f"{report['certificate']:.4f}"
        act_str = f"{report['action']}"

        print(f"{epoch:<6} | {v_str:<10} | {stat_str:<15} | {cert_str:<12} | {act_str}")
        time.sleep(0.05)

    print("-" * 75)
    print("\n[Phase 3] Economic Cost Summary:")
    summary = engine.cost_model.summary()

    # Compare against traditional periodic recalibration (every 5 epochs)
    periodic_cals = num_epochs // 5
    periodic_shots = num_epochs * 4096
    periodic_cost = (periodic_cals * 100.0) + (periodic_shots * 0.0001)

    sym_cost = summary["total_cost"]
    savings_pct = (periodic_cost - sym_cost) / periodic_cost * 100

    print(f"  • Periodic Recalibration Baseline Cost: ${periodic_cost:.2f}")
    print(f"  • SymSentinel Total Expenditure:       ${sym_cost:.2f}")
    print(f"  • NET COST SAVINGS:                    {savings_pct:.1f}%")
    print(f"  • Total Calibrations Run:              {int(summary['calibrations'])} (vs {periodic_cals} periodic)")
    print(f"  • Quantum Shots Used:                  {int(summary['shots'])} (vs {periodic_shots} periodic)")
    print("=" * 75)


if __name__ == "__main__":
    main()
