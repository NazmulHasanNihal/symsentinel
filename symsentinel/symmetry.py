"""Symmetry Characterization, Closed-Form Violation Laws & SPAM Deconfounding.

Implements Research Plan v5.0 Section 3 & 5:
  1. Exact Z2 parity violation law:
     nu_t^{Z2}(p_t, r_t) = 1/2 * [1 - (1 - 2*p_t)^d * (1 - 2*r_t)^n]
  2. Exact U(1) excitation charge-leakage generating polynomial law:
     P_d(z) = [(1 - p_t) + p_t/2 * (z + z^-1)]^d
     nu_t^{U(1)}(p_t, r_t) = 1 - [z^0] P_d(z) * (1 - r_t)^n
  3. 0-depth SPAM readout probe for isolating readout drift r_t from gate fault drift p_t.
"""

from typing import List, Optional, Sequence, Tuple, Union
import numpy as np
from math import comb


def z2_parity_violation_rate(
    p_gate: float,
    r_readout: float,
    depth: int,
    num_qubits: int,
) -> float:
    r"""Exact closed-form Z2 parity violation rate:

        \nu_t(p_t, r_t) = \frac{1}{2} [1 - (1 - 2 p_t)^d (1 - 2 r_t)^n]

    Parameters:
        p_gate: Physical fault probability per gate layer p_t.
        r_readout: Physical readout error probability per qubit r_t.
        depth: Circuit depth in gate layers d.
        num_qubits: Number of measured qubits n.
    """
    p = float(np.clip(p_gate, 0.0, 0.5))
    r = float(np.clip(r_readout, 0.0, 0.5))
    gate_factor = (1.0 - 2.0 * p) ** depth
    readout_factor = (1.0 - 2.0 * r) ** num_qubits
    return float(0.5 * (1.0 - gate_factor * readout_factor))


def u1_charge_leakage_rate(
    p_gate: float,
    r_readout: float,
    depth: int,
    num_qubits: int,
) -> float:
    r"""Exact U(1) particle/excitation number leakage probability.

    Evaluates the Laurent generating polynomial constant term:
        P_d(z) = [(1 - p) + \frac{p}{2}(z + z^{-1})]^d
        [z^0] P_d(z) = \sum_{k=0}^{\lfloor d/2 \rfloor} \binom{d}{2k} \binom{2k}{k} (1 - p)^{d-2k} (p/2)^{2k}
    Combined with readout fidelity:
        \nu_t^{U(1)} = 1 - [z^0] P_d(z) \cdot (1 - r_t)^n
    """
    p = float(np.clip(p_gate, 0.0, 0.5))
    r = float(np.clip(r_readout, 0.0, 0.5))
    
    # Constant term of charge random walk
    p0 = sum(
        comb(depth, 2 * k) * comb(2 * k, k) * ((1.0 - p) ** (depth - 2 * k)) * ((p / 2.0) ** (2 * k))
        for k in range(depth // 2 + 1)
    )
    readout_retention = (1.0 - r) ** num_qubits
    return float(1.0 - p0 * readout_retention)


def invert_gate_error_from_violation(
    nu_measured: float,
    r_readout: float,
    depth: int,
    num_qubits: int,
) -> float:
    r"""Inverts the closed-form Z2 law to extract physical gate error p_t:

        (1 - 2 p_t)^d = \frac{1 - 2 \nu_t}{(1 - 2 r_t)^n}
        \implies p_t = \frac{1}{2} [1 - (\frac{1 - 2 \nu_t}{(1 - 2 r_t)^n})^{1/d}]
    """
    r = float(np.clip(r_readout, 0.0, 0.499))
    readout_term = (1.0 - 2.0 * r) ** num_qubits
    ratio = (1.0 - 2.0 * nu_measured) / max(readout_term, 1e-6)
    ratio = max(0.0, min(1.0, ratio))
    gate_retention = ratio ** (1.0 / max(1, depth))
    p_inferred = 0.5 * (1.0 - gate_retention)
    return float(np.clip(p_inferred, 0.0, 0.5))


def zero_depth_spam_probe(measured_bitstrings: Union[np.ndarray, Sequence[str]]) -> float:
    r"""0-depth SPAM readout probe for isolating readout error r_t.

    Prepares |0>^{\otimes n} and immediately measures computational basis bitstrings
    with depth d = 0 (zero gate error).
    The empirical bit-flip fraction directly estimates physical readout noise:
        \hat{r}_t = \frac{1}{n \cdot K} \sum_{k=1}^K \sum_{j=1}^n x_j^{(k)}
    """
    if len(measured_bitstrings) == 0:
        return 0.0
    if isinstance(measured_bitstrings, (list, tuple)) and isinstance(measured_bitstrings[0], str):
        arr = np.array([[int(c) for c in b] for b in measured_bitstrings], dtype=np.float64)
    else:
        arr = np.asarray(measured_bitstrings, dtype=np.float64)
    
    return float(np.mean(arr))

