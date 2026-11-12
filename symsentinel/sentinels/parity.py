"""Z2 Parity Sentinel.

Evaluates bit-parity conservation across full or partial qubit registers
from computational basis measurement shots at zero extra shot cost.
"""

from typing import Optional, Sequence, Union
import numpy as np
from symsentinel.sentinels.base import BaseSentinel


class Z2ParitySentinel(BaseSentinel):
    r"""Monitors Z2 parity symmetry (e.g., Pi_Z = Z \otimes ... \otimes Z).

    Parameters:
        num_qubits: Total number of qubits in the register.
        target_parity: Expected parity sector, 0 for even (sum mod 2 == 0), 1 for odd.
        qubit_indices: Optional subset of qubits defining the symmetry operator.
                       Defaults to all qubits.
    """

    def __init__(
        self,
        num_qubits: int,
        target_parity: int = 0,
        qubit_indices: Optional[Sequence[int]] = None,
        name: str = "Z2_Parity",
    ):
        super().__init__(name=name, num_qubits=num_qubits)
        if target_parity not in (0, 1):
            raise ValueError("target_parity must be 0 (even) or 1 (odd).")
        self.target_parity = target_parity
        self.qubit_indices = list(qubit_indices) if qubit_indices is not None else list(range(num_qubits))

    def evaluate_bitstring(self, bitstring: Union[str, Sequence[int], np.ndarray]) -> int:
        """Returns 1 if the bitstring violates target parity on the selected qubits, else 0."""
        if isinstance(bitstring, str):
            # Parse bitstring string e.g. "0101"
            total = sum(int(bitstring[i]) for i in self.qubit_indices)
        elif isinstance(bitstring, (list, tuple, np.ndarray)):
            total = sum(int(bitstring[i]) for i in self.qubit_indices)
        else:
            raise TypeError(f"Unsupported bitstring type: {type(bitstring)}")

        parity = total % 2
        return 1 if parity != self.target_parity else 0
