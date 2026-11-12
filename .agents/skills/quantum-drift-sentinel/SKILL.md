---
name: quantum-drift-sentinel
description: Models, simulates, and analyzes quantum hardware drift, symmetry conservation sentinels, Pauli Transfer Matrix (PTM) leakage, and free syndrome extraction. Use when implementing equivariant quantum circuits, simulating T1/T2 noise fluctuations, or analyzing blind spots of symmetry verification.
license: Apache-2.0
allowed-tools: Run Command, Read File, Write File
metadata:
  version: "1.0"
  skill-author: SymSentinel Core
---

# Quantum Hardware Drift & Symmetry Sentinels

## When to Use
Use this skill when designing symmetric quantum learners, modeling non-stationary quantum hardware drift ($T_1, T_2$, coherent over-rotations, crosstalk), extracting free symmetry syndromes from measurement bitstrings, and calculating blind spots of symmetry sentinels.

## Core Concepts

### 1. Symmetry Families in Quantum Circuits
A quantum state $\rho$ and circuit $U(\theta)$ respect a symmetry group $G$ if:
$$[U_g, U(\theta)] = 0 \quad \text{and} \quad U_g |\psi_0\rangle = e^{i\phi_g} |\psi_0\rangle \quad \forall g \in G$$
Three canonical symmetry families used in SymSentinel:
1. **$\mathbb{Z}_2$ Parity Symmetry:**
   - Generator: $\Pi_Z = \bigotimes_{j=1}^n Z_j$.
   - Conserved eigenspaces: Even ($\Pi_Z = +1$) vs Odd ($\Pi_Z = -1$).
   - Computational basis syndrome for bitstring $x \in \{0, 1\}^n$:
     $$s(x) = \left(\sum_{j=1}^n x_j\right) \bmod 2$$
2. **$U(1)$ Particle / Excitation Conservation:**
   - Generator: $\hat{N} = \sum_{j=1}^n \frac{I - Z_j}{2}$ (Hamming weight).
   - Conserved subspace: Constant Hamming weight subspace $\mathcal{H}_k = \text{span}\{|x\rangle : |x| = k\}$.
   - Syndrome: $s(x) = \mathbb{I}(|x| \ne k)$.
3. **$\mathbb{Z}_2 \times \mathbb{Z}_2$ Symmetry:**
   - Simultaneous conservation of two independent parity operators (e.g. subsystem parities or spatial reflection + spin flip).

### 2. Free Sentinel Syndrome Extraction (Zero Shot Cost)
In standard quantum machine learning, computational basis measurements $x^{(1)}, \dots, x^{(K)} \sim p(x \mid \theta)$ are collected to evaluate observable expectation values.
**Free Sentinel Principle:**
Instead of injecting extra sentinel circuits, compute the empirical symmetry violation directly from the same $K$ shots:
$$\hat{V}_t = \frac{1}{K} \sum_{k=1}^K s\left(x_t^{(k)}\right)$$
Under nominal noiseless or calibrated pre-change conditions, $\mathbb{E}[\hat{V}_t] = v_0 \approx 0$.
Under hardware drift breaking the symmetry, $\mathbb{E}[\hat{V}_t] > v_0$.

### 3. Noise Drift Regimes
Simulate three distinct drift profiles:
- **D1 (Coherent / Unitary Drift):** Slowly fluctuating single-qubit phase over-rotations $R_z(\theta + \delta_t)$ and two-qubit $ZZ$ crosstalk $\exp(-i \chi_t Z_j Z_k)$.
- **D2 (Incoherent / Dissipative Drift):** Drifting relaxation rates $1/T_1(t)$ (amplitude damping) and dephasing rates $1/T_2(t)$ (phase damping).
- **D3 (Mixed / Jump Drift):** Two-level system (TLS) defect collisions producing abrupt telegraph noise jumps.

### 4. The Blind-Spot Theorem (RQ2 / Gate G2)
**Theorem (Symmetry-Covariant Blind Spot):**
If a noise channel $\mathcal{E}$ commutes with all group generators:
$$\mathcal{E}(U_g \rho U_g^\dagger) = U_g \mathcal{E}(\rho) U_g^\dagger \quad \forall g \in G$$
then $\mathcal{E}$ preserves the invariant subspaces of $G$, and:
$$\mathbb{E}[\hat{V}_t \mid \mathcal{E}] = \mathbb{E}[\hat{V}_t \mid \text{Noiseless}] = 0$$
Even if $\mathcal{E}$ depolarizes the state or degrades learning performance by $\Delta \mathcal{R} > 0$, the symmetry sentinel **provably cannot detect it**.
*Concrete Example:* For $\mathbb{Z}_2$ parity $\prod Z_j$, collective dephasing $\mathcal{E}_{dephase}(\rho) = (1-p)\rho + p Z^{\otimes n} \rho Z^{\otimes n}$ commutes with parity and is completely invisible to the sentinel.

