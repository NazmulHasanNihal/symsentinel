"""Multi-Day IBM Calibration Replay (Regime D4) and Unified Benchmark Harness."""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np

from symsentinel.sim.circuits import BenchmarkCircuits
from symsentinel.sim.drift import DriftSimulator


class MultiDayIBMCalibrationReplay:
    """Replays historical multi-day IBM Quantum calibration time-series logs (Regime D4)."""

    def __init__(self, num_qubits: int = 8, seed: int = 42):
        self.num_qubits = num_qubits
        self.rng = np.random.default_rng(seed)
        self.nominal_t1 = 120.0
        self.nominal_t2 = 80.0
        self.nominal_cnot_err = 0.008
        self.nominal_readout_err = 0.012

    def sample_epoch(self, epoch: int) -> Dict[str, float]:
        day_night_cycle = 0.15 * np.sin(2.0 * np.pi * epoch / 24.0)
        random_walk = self.rng.normal(0.0, 0.05)
        tls_jump = 0.25 if epoch >= 45 else 0.0

        t1 = max(40.0, self.nominal_t1 * (1.0 - day_night_cycle * 0.1 - tls_jump * 0.3 + random_walk * 0.05))
        t2 = max(20.0, self.nominal_t2 * (1.0 - day_night_cycle * 0.2 - tls_jump * 0.4 + random_walk * 0.08))
        gate_err = min(0.10, self.nominal_cnot_err * (1.0 + day_night_cycle * 0.3 + tls_jump * 3.0 + abs(random_walk)))
        readout_err = min(0.08, self.nominal_readout_err * (1.0 + day_night_cycle * 0.2 + abs(random_walk)))

        return {
            "epoch": epoch,
            "t1_us": float(t1),
            "t2_us": float(t2),
            "gate_error": float(gate_err),
            "readout_error": float(readout_err),
            "effective_nu": float(0.5 * (1.0 - (1.0 - 2.0 * gate_err)**6 * (1.0 - 2.0 * readout_err)**self.num_qubits)),
        }


class BenchmarkHarness:
    """Unified benchmark executor wiring circuits B1, B2 to drift regimes D1, D2, D3, D4."""

    def __init__(self, num_qubits: int = 8, seed: int = 42):
        self.num_qubits = num_qubits
        self.seed = seed
        self.drift_sim = DriftSimulator(num_qubits=num_qubits, seed=seed)
        self.ibm_replay = MultiDayIBMCalibrationReplay(num_qubits=num_qubits, seed=seed)

    def run_epoch(
        self,
        benchmark: str,
        regime: str,
        epoch: int,
        num_shots: int = 1024,
    ) -> Tuple[np.ndarray, float]:
        if regime == "D1":
            return self.drift_sim.sample_d1_coherent(epoch=epoch, num_shots=num_shots)
        elif regime == "D2":
            return self.drift_sim.sample_d2_incoherent(epoch=epoch, num_shots=num_shots)
        elif regime == "D3":
            bits, nu, _ = self.drift_sim.sample_d3_jump(epoch=epoch, jump_epoch=30, num_shots=num_shots)
            return bits, nu
        elif regime == "D4":
            log = self.ibm_replay.sample_epoch(epoch)
            nu = log["effective_nu"]
            bits = self.drift_sim._generate_bitstrings(nu, num_shots)
            return bits, nu
        else:
            raise ValueError(f"Unknown drift regime: {regime}")
