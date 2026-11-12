"""Abstract Base Class for Symmetry Sentinels."""

from abc import ABC, abstractmethod
from typing import Sequence, Union
import numpy as np


class BaseSentinel(ABC):
    """Base class for extracting hardware drift syndromes from measurement bitstrings."""

    def __init__(self, name: str, num_qubits: int):
        self.name = name
        self.num_qubits = num_qubits

    @abstractmethod
    def evaluate_bitstring(self, bitstring: Union[str, Sequence[int], np.ndarray]) -> int:
        """Evaluate a single computational basis bitstring.

        Returns:
            0 if the bitstring respects the symmetry sector,
            1 if the bitstring violates the symmetry (syndrome = 1).
        """
        pass

    def evaluate_batch(self, bitstrings: Sequence[Union[str, Sequence[int], np.ndarray]]) -> np.ndarray:
        """Evaluate an ensemble of measurement bitstrings (shots).

        Returns:
            1D numpy array of binary violation indicators (0 or 1) of length K.
        """
        return np.array([self.evaluate_bitstring(b) for b in bitstrings], dtype=np.int32)

    def violation_rate(self, bitstrings: Sequence[Union[str, Sequence[int], np.ndarray]]) -> float:
        """Compute the empirical violation rate across K shots:

            V = (1 / K) * sum_k s(x^(k))

        Returns:
            float in [0.0, 1.0].
        """
        if len(bitstrings) == 0:
            return 0.0
        return float(np.mean(self.evaluate_batch(bitstrings)))

