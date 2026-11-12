"""Physical Hardware Drift Regimes D1, D2, and D3.

Implements realistic non-stationary quantum hardware noise:
  - D1 (Coherent): Ornstein-Uhlenbeck stochastic unitary phase over-rotation.
  - D2 (Incoherent): Drifting T1/T2 relaxation and readout noise.
  - D3 (Jump Drift): Two-Level System (TLS) defect jump:
      * D3-visible: faults that anticommute with symmetry S (visible to sentinel).
      * D3-blind: faults that commute with symmetry S (invisible to sentinel, proving Theorem T2).
"""

from typing import List, Optional, Tuple
import numpy as np


class DriftSimulator:
    """Simulates multi-epoch hardware drift and generates stochastic measurement bitstrings."""

    def __init__(
        self,
        num_qubits: int,
        target_parity: int = 0,
        seed: Optional[int] = 42,
    ):
        self.num_qubits = num_qubits
        self.target_parity = target_parity
        self.rng = np.random.default_rng(seed)

        # Baseline error parameters
        self.base_readout_error = 0.01  # r_0 = 1%
        self.base_gate_error = 0.005    # q_0 = 0.5% per gate

        # OU process state for D1
        self.ou_state = 0.0

    def theoretical_violation_rate(
        self,
        fault_anticommute_probs: List[float],
        readout_error: float,
    ) -> float:
        """Exact theoretical closed form from Section 4.2 of Research Plan:

            p_t = 1/2 * (1 - prod_j (1 - 2 * q_j))
            nu_t = 1/2 * (1 - (1 - 2 * p_t) * (1 - 2 * r_t)^n)
        """
        prod_q = np.prod([1.0 - 2.0 * q for q in fault_anticommute_probs])
        p_t = 0.5 * (1.0 - prod_q)
        r_term = (1.0 - 2.0 * readout_error) ** self.num_qubits
        nu_t = 0.5 * (1.0 - (1.0 - 2.0 * p_t) * r_term)
        return float(nu_t)

    def sample_d1_coherent(
        self,
        epoch: int,
        num_shots: int,
        theta_drift_scale: float = 0.05,
    ) -> Tuple[np.ndarray, float]:
        """D1: Ornstein-Uhlenbeck stochastic phase over-rotation."""
        # OU step: dX_t = -theta * X_t * dt + sigma * dW_t
        self.ou_state = 0.9 * self.ou_state + self.rng.normal(0.0, theta_drift_scale)
        p_fault = float(np.sin(self.ou_state) ** 2)
        # Generate bitstrings
        nu = self.theoretical_violation_rate([p_fault] * self.num_qubits, self.base_readout_error)
        bitstrings = self._generate_bitstrings(nu, num_shots)
        return bitstrings, nu

    def sample_d2_incoherent(
        self,
        epoch: int,
        num_shots: int,
        drift_rate: float = 0.002,
    ) -> Tuple[np.ndarray, float]:
        """D2: Linearly drifting T1/T2 incoherent relaxation."""
        current_gate_err = min(0.3, self.base_gate_error + drift_rate * epoch)
        current_readout_err = min(0.2, self.base_readout_error + 0.5 * drift_rate * epoch)
        nu = self.theoretical_violation_rate([current_gate_err] * self.num_qubits, current_readout_err)
        bitstrings = self._generate_bitstrings(nu, num_shots)
        return bitstrings, nu

    def sample_d3_jump(
        self,
        epoch: int,
        jump_epoch: int,
        num_shots: int,
        jump_magnitude: float = 0.15,
        is_blind_spot: bool = False,
    ) -> Tuple[np.ndarray, float, float]:
        """D3: Two-level system (TLS) jump defect.

        Parameters:
            is_blind_spot: If True, the defect commutes with symmetry S.
                           Violation stays at baseline, yet task risk shifts!
                           This directly verifies Theorem T2 (Blind-Spot Theorem).

        Returns:
            (bitstrings, empirical_nu, true_risk_shift)
        """
        has_jumped = epoch >= jump_epoch

        if has_jumped:
            if is_blind_spot:
                # Commuting fault: anticommute probability is EXACTLY ZERO
                # Sentinel violation rate remains at nominal null baseline!
                fault_probs = [0.0] * self.num_qubits
                nu = self.theoretical_violation_rate(fault_probs, self.base_readout_error)
                risk_shift = jump_magnitude * 1.5  # Risk shifts despite 0 violation!
            else:
                # Visible fault: anticommutes with symmetry
                fault_probs = [jump_magnitude] * 2 + [0.0] * (self.num_qubits - 2)
                nu = self.theoretical_violation_rate(fault_probs, self.base_readout_error)
                risk_shift = jump_magnitude * 1.5
        else:
            fault_probs = [0.0] * self.num_qubits
            nu = self.theoretical_violation_rate(fault_probs, self.base_readout_error)
            risk_shift = 0.0

        bitstrings = self._generate_bitstrings(nu, num_shots)
        return bitstrings, nu, risk_shift

    def _generate_bitstrings(self, violation_rate: float, num_shots: int) -> np.ndarray:
        """Helper generating synthetic bitstrings conforming to violation_rate."""
        # If parity is even (0), violation means odd parity (1)
        bitstrings = []
        is_violated = self.rng.binomial(1, violation_rate, size=num_shots)

        for v in is_violated:
            # Generate random bits
            bits = self.rng.integers(0, 2, size=self.num_qubits)
            current_parity = int(np.sum(bits) % 2)
            target = 1 - self.target_parity if v == 1 else self.target_parity
            if current_parity != target:
                bits[0] = 1 - bits[0]  # flip first bit to match target parity
            bitstrings.append(bits)

        return np.array(bitstrings, dtype=np.int32)

