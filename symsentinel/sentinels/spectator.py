"""Universal Spectator & Ancilla Sentinel.

Enables drift monitoring for arbitrary quantum circuits (including non-symmetric
ansätze and generic QNNs) by monitoring dedicated spectator/ancilla channels.
"""

from typing import Sequence, Union
import numpy as np
from symsentinel.sentinels.base import BaseSentinel


class SpectatorSentinel(BaseSentinel):
    """Monitors drift on dedicated spectator/ancilla qubits.

    In a circuit with N computational qubits and M spectator qubits,
    the spectator qubits are prepared in a known probe state (e.g., |00...0>
    or Bell pairs) and subjected to idling during computational execution.
    Any excitation, dephasing, or crosstalk flips the spectator syndrome.

    Parameters:
        num_qubits: Total number of qubits (computational + spectator).
        spectator_indices: Indices of spectator qubits in the measured register.
        expected_state: Expected binary state of spectator qubits (e.g., [0, 0]).
    """

    def __init__(
        self,
        num_qubits: int,
        spectator_indices: Sequence[int],
        expected_state: Sequence[int] = (0,),
        name: str = "Spectator_Sentinel",
    ):
        super().__init__(name=name, num_qubits=num_qubits)
        if len(spectator_indices) != len(expected_state):
            raise ValueError("spectator_indices and expected_state must have the same length.")
        self.spectator_indices = list(spectator_indices)
        self.expected_state = list(expected_state)

    def evaluate_bitstring(self, bitstring: Union[str, Sequence[int], np.ndarray]) -> int:
        """Returns 1 if any spectator qubit deviated from its expected state, else 0."""
        for q_idx, exp_val in zip(self.spectator_indices, self.expected_state):
            bit_val = int(bitstring[q_idx])
            if bit_val != exp_val:
                return 1
        return 0

