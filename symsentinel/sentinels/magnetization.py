"""U(1) Magnetization & Particle Number Sentinel.

Monitors conservation of total excitation number / Hamming weight in
computational basis shots (e.g., in quantum chemistry or XXZ spin chains).
"""

from typing import Optional, Sequence, Union
import numpy as np
from symsentinel.sentinels.base import BaseSentinel


class U1MagnetizationSentinel(BaseSentinel):
    """Monitors U(1) particle number conservation (e.g., fixed Hamming weight k).

    Parameters:
        num_qubits: Total number of qubits in the circuit.
        target_weight: Expected number of |1> states (excitation number k).
        qubit_indices: Optional subset of qubits defining the conservation region.
    """

    def __init__(
        self,
        num_qubits: int,
        target_weight: int,
        qubit_indices: Optional[Sequence[int]] = None,
        name: str = "U1_Magnetization",
    ):
        super().__init__(name=name, num_qubits=num_qubits)
        if target_weight < 0 or target_weight > num_qubits:
            raise ValueError(f"target_weight must be in [0, {num_qubits}], got {target_weight}.")
        self.target_weight = target_weight
        self.qubit_indices = list(qubit_indices) if qubit_indices is not None else list(range(num_qubits))

    def evaluate_bitstring(self, bitstring: Union[str, Sequence[int], np.ndarray]) -> int:
        """Returns 1 if the bitstring Hamming weight != target_weight, else 0."""
        if isinstance(bitstring, str):
            weight = sum(int(bitstring[i]) for i in self.qubit_indices)
        elif isinstance(bitstring, (list, tuple, np.ndarray)):
            weight = sum(int(bitstring[i]) for i in self.qubit_indices)
        else:
            raise TypeError(f"Unsupported bitstring type: {type(bitstring)}")

        return 0 if weight == self.target_weight else 1

