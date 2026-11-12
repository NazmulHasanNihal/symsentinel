---
name: anytime-valid-inference
description: Formulates, implements, and mathematically verifies safe anytime-valid sequential inference (SAVI), e-processes, e-detectors, test martingales, and conformal risk control (CRC). Use when building sequential stopping rules, bounding false alarms under continuous monitoring, proving Ville's inequality bounds, or controlling risk under distribution drift.
license: Apache-2.0
allowed-tools: Run Command, Read File, Write File
metadata:
  version: "1.0"
  skill-author: SymSentinel Core
---

# Anytime-Valid Inference & Sequential Testing

## When to Use
Use this skill when designing, proving, or simulating sequential stopping rules, drift detectors, e-processes, and conformal risk bounds that must remain mathematically valid under continuous monitoring, optional stopping, and optional continuation.

## Mathematical Core

### 1. Test Martingales & Ville's Inequality
A test martingale $(M_t)_{t \ge 0}$ adapted to filtration $(\mathcal{F}_t)$ satisfies:
$$M_0 = 1, \quad M_t \ge 0, \quad \mathbb{E}_P[M_t \mid \mathcal{F}_{t-1}] \le M_{t-1} \quad \forall P \in \mathcal{P}_0$$
By Ville's inequality, for any threshold $1/\alpha > 0$:
$$\mathbb{P}_P\left(\exists t \ge 1: M_t \ge \frac{1}{\alpha}\right) \le \alpha$$
This guarantees that stopping at any data-dependent time $\tau$ retains rigorous Type-I error control without $p$-value corrections.

### 2. E-Detectors for Sequential Change Detection
For pre-change null class $\mathcal{P}_0$, an **e-detector** $D_t$ is a nonnegative adapted process satisfying:
$$\mathbb{E}_P[D_\tau] \le \mathbb{E}_P[\tau] \quad \text{for all stopping times } \tau \text{ and } P \in \mathcal{P}_0$$
Declaring a change at $T_b = \inf\{ t \ge 1: D_t \ge b \}$ guarantees:
1. **Average Run Length (ARL) Control:**
   $$\inf_{P \in \mathcal{P}_0} \mathbb{E}_P[T_b] \ge b$$
2. **Optional-Horizon Inequality (No Early False Alarms):**
   $$\mathbb{P}_P(T_b \le \sigma) \le \frac{\mathbb{E}_P[\sigma]}{b} \quad \text{for any stopping horizon } \sigma$$

### 3. Nonparametric Betting Martingales
For bounded observations $X_t \in [0, 1]$ under null mean $\mu \in [0, 1]$:
$$M_t = \prod_{i=1}^t \Big(1 + \lambda_i (X_i - \mu)\Big)$$
**Predictability Requirement:** The betting fraction $\lambda_i \in [-1/(1-\mu), 1/\mu]$ must be **strictly $\mathcal{F}_{i-1}$-measurable** (computed only from $X_1, \dots, X_{i-1}$, never using $X_i$).
Recommended empirical variance tuning:
$$\lambda_i = \min\left(c, \sqrt{\frac{2 \log(2/\alpha)}{i \cdot (\hat{\sigma}_{i-1}^2 + \epsilon)}}\right)$$

### 4. Anytime-Valid Conformal Risk Control (A-CRC)
Given loss $L_t \in [0, B]$ and risk threshold $\alpha$:
- Set-valued predictor $C_\theta(X_t)$ controlled by calibration parameter $\theta_t$.
- Track excess loss e-process $E_t = \prod_{i=1}^t (1 + \eta_i (L_i - \alpha))$.
- Recalibrate whenever $E_t \ge 1/\delta$, ensuring risk violation probability $\le \delta$.

## Verification Checklist
Before approving any sequential statistical implementation:
- [ ] **Filtration check:** Verify no lookahead bias in $\lambda_t$.
- [ ] **Nonnegativity check:** Ensure $1 + \lambda_t (X_t - \mu) \ge 0$ almost surely.
- [ ] **Monte Carlo Null Calibration:** Run at least 1,000 null trajectories; measured false alarm rate must satisfy $\le 1/b$.
- [ ] **Detection Delay Audit:** Measure average detection delay under step and ramp drift regimes.

