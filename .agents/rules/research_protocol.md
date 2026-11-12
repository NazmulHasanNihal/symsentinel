# Research Protocol & Quality Assurance Rules

## 1. Literature Citation & Gap Verification
- Never claim a prior work "fails to address X" without checking the exact full text using `scripts/search_papers.py`.
- Always record:
  - Exact arXiv ID and version.
  - Section and equation/theorem number in the cited paper.
  - Assumptions under which their theorem holds (e.g., i.i.d., bounded support, single vs composite null).

## 2. Martingale Verification Rules
Any implementation of an e-process, test martingale, or e-detector must undergo a 3-stage validation suite:
1. **Algebraic / Nonnegativity Test:**
   - Assert $M_t \ge 0$ for all possible observation values $X_t \in \text{supp}(X)$.
   - Assert $\lambda_t \in (-1/(1-\mu), 1/\mu)$.
2. **Predictability Test:**
   - Unit test verifying $\lambda_t$ does not change if future values $X_t, X_{t+1}, \dots$ are mutated.
3. **Null Empirical Expectation Test:**
   - Over 1,000 independent null simulations:
     $$\hat{\mathbb{E}}[M_\tau] \le 1.0 + 3 \times \text{SE}$$
   - For e-detectors at threshold $b$: measured false-alarm rate $\le 1/b$.

## 3. Drift & Physics Simulation Rules
- Symmetries $\mathbb{Z}_2$, $U(1)$, and $\mathbb{Z}_2 \times \mathbb{Z}_2$ must be verified under noiseless conditions (syndrome violation $\equiv 0$).
- When comparing to baselines (periodic recalibration, fixed-threshold CUSUM, unmitigated), run on identical seed sequences and noise traces.
- Report both statistical efficiency (detection delay, false alarm rate) and economic efficiency (total shot count + calibration cost).

