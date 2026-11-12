# SymSentinel — Paper 4 Research Plan v4

Nov 8, 2026 · Nazmul Hasan Nihal

## 1. Executive charter

SymSentinel is a ten-week plan to build an anytime-valid, cost-aware rule for deciding when a symmetric quantum learner must be recalibrated, using symmetry violations that the hardware already produces in every run.

- **Working title:** SymSentinel: Anytime-Valid Recalibration of Symmetric Quantum Learners from Free Symmetry Syndromes under Hardware Drift.
- **Core claim:** a symmetric circuit turns its own conservation law into a drift sensor at near-zero extra shot cost, and that sensor can drive a recalibration rule with a proven false-alarm guarantee, a certified risk bound, and a proven limit on what it cannot see.
- **Fields:** quantum machine learning reliability, sequential statistics (e-processes and e-detectors), symmetry-aware quantum learning, quantum hardware drift.
- **Target venues:** Quantum (primary); IEEE Transactions on Quantum Engineering and npj Quantum Information (alternatives). An ML venue such as AISTATS or UAI is possible if the statistics framing leads. ICML and NeurIPS would need a stronger learning result than this plan promises.
- **Open-source artifact:** Python package `symsentinel` (PennyLane, Qiskit Aer, qiskit-ibm-runtime) with a Zenodo DOI.
- **Overlap rule:** no QEC decoders, no biology, no graph AML. The only link to Paper 1 is the martingale and conformal machinery.

### Changes from Q-RACE v3.0

| Component | Q-RACE v3.0 | SymSentinel v4 |
| --- | --- | --- |
| Drift sensor | Extra light-cone sentinel circuits | Symmetry syndrome read from the same shots |
| Sensor-to-risk link | Analytic Pauli-transfer factor, unprovable in practice | Rigorous leakage bound plus a calibrated monotone map |
| Controller | 5-action contextual bandit with regret theorem | 2-action stopping rule (recalibrate or continue) |
| Theory | 4 theorems, 2 propositions | 4 targeted results, one of them a detectability limit |
| Benchmarks | 3 mixed tasks | 3 symmetry families: Z2, U(1), Z2 x Z2 |
| Schedule | 5 weeks | 10 weeks with gates |

## 2. Novelty boundary

The claim is deliberately narrow: no work I found combines a free symmetry sentinel, an anytime-valid detector, a cost-aware recalibration decision, and a characterized blind spot. Each piece alone has prior art, so the paper must credit all of it.

| Closest work | What it does | What it lacks relative to this plan |
| --- | --- | --- |
| [eSCD, Zecchin, Simeone, Ramdas (Feb 2026)](https://arxiv.org/pdf/2602.11846) | E-detector for quantum changepoints on observables, using classical shadows | No link to task risk, no recalibration cost, no symmetry sentinel |
| [Adaptive Quantum Conformal Prediction (Nov 2025)](https://arxiv.org/pdf/2511.18225) | Online recalibration of conformal coverage under non-stationary noise | Controls coverage, not when to recalibrate hardware; no symmetry |
| [Blind symmetry matching (Jun 2026)](https://arxiv.org/pdf/2606.19196) | Discovers symmetry to cut shots when estimating a target | Not used for drift monitoring |
| [GUESS (2026)](https://arxiv.org/pdf/2603.13060) and [symmetry-adjusted shadows](https://arxiv.org/abs/2310.03071v1) | Use symmetry decay for error mitigation and post-selection | No detection guarantee, no recalibration rule |
| [Runtime calibration as feedback control (May 2026)](https://www.emergentmind.com/papers/2605.11860) | Recalibration as a costly reset in a control problem | No risk guarantee, no sensor design |
| [SPARTA (Nov 2025)](https://arxiv.org/pdf/2511.19551) and [shot-budget CRC benchmark (NeurIPS 2026)](https://neurips.cc/virtual/2026/173906) | Risk-controlled shot scheduling for variational algorithms | No symmetry, no calibration decisions |
| [Non-exchangeable CRC (ICLR 2024)](https://arxiv.org/pdf/2310.01262), [e-detectors (Shin, Ramdas, Rinaldo)](https://arxiv.org/pdf/2203.03532) | Statistical tools this plan builds on | Not quantum-specific |

**Precise claim:** the first anytime-valid, symmetry-based, cost-aware recalibration rule for symmetric quantum learners, together with a theorem stating which noise it provably cannot detect.

**Not claimed:** quantum advantage, coverage of all noise types, or novelty of e-detectors themselves.

**Caveat:** my prior-art search was limited to a few queries. Gate G0 repeats it with a fixed protocol (section 3) before any further work.

## 3. Research questions, hypotheses and gates

Five questions (RQ0 to RQ4) drive the work, each with a pre-registered pass threshold, and gate Gk checks RQk. A failed gate triggers the fallback in section 10 instead of silently changing the claim.

| ID | Question | Hypothesis | Pass threshold | Week |
| --- | --- | --- | --- | --- |
| RQ0 | Is the gap real? | No published work combines the four elements | Fixed-protocol search finds none; all 6 unit tests pass | 1 |
| RQ1 | Is the free-sentinel detector valid? | Predictable shot counts keep the e-detector ARL at or above its target | Measured false-alarm rate at most 1/500 per epoch over 1000 null runs; detection delay within 2x of theory | 3 |
| RQ2 | What can symmetry violation not see? | Noise covariant with the symmetry gives zero violation yet can shift risk | Closed-form violation formula matches simulation within 3 standard errors; blind-spot example confirmed | 5 |
| RQ3 | Is the calibrated risk link valid? | A monotone map plus an exceedance e-process bounds risk shift anytime | Violation rate at most 0.05 under drift regimes D1 to D3; periodic baseline violates by more than 2x | 7 |
| RQ4 | Does it save cost? | The cost-aware threshold beats fixed schedules at equal certified risk | At least 25% lower total cost (calibration plus shots) than the best periodic or threshold baseline | 9 |

### Prior-art protocol for G0

1. Search arXiv, Google Scholar and Semantic Scholar with at least 12 query combinations of: symmetry violation, parity, conserved charge, syndrome, drift detection, recalibration, anytime-valid, e-process, conformal, certificate.
2. Check forward citations of the papers listed in section 2.
3. Record every hit and its decision in a short log kept with the repository.
4. Set arXiv and Scholar alerts for the same terms, and re-run the search before submission.

## 4. Mathematical framework

The framework has five parts: a symmetric learner, a symmetry-violation stream, an e-detector on that stream, a map from violation to risk shift, and a cost-aware stopping rule. Validity of the risk certificate never depends on the detector; the detector only decides when to pay for recalibration.

### 4.1 Setting

At epochs t = 1, 2, ..., T the learner holds parameters θ_t of a circuit U_θ(x) built only from gates that commute with a symmetry operator S (for example S = product of X over all qubits for TFIM, or total Z magnetization for XXZ). Inputs are prepared inside a known symmetry sector. The hardware channel E_t drifts. The task loss ℓ takes values in [0, 1], and R_t(θ_t) is the population risk at epoch t. A calibration action resets the hardware error state at cost c_cal and starts a new calibration era k.

### 4.2 The symmetry-violation stream

Each epoch uses S_t shots, chosen before the epoch begins. The sentinel is the fraction of shots whose measured symmetry value is violated, which lies in [0, 1]. If p_t is the true out-of-sector weight and r_t the per-qubit readout flip rate, then for a parity symmetry on n qubits the mean of the stream is:

```latex
\nu_t = \mathbb{E}[z_t \mid \mathcal{F}_{t-1}] = \tfrac{1}{2}\Big(1 - (1 - 2p_t)\,(1 - 2r_t)^{n}\Big)
```

Readout drift therefore also moves the stream. A cheap readout-only sentinel separates the two causes. When every gate commutes with S and faults are independent Pauli faults, a fault j that anticommutes with S flips the symmetry value, and the faults combine as:

```latex
p_t = \tfrac{1}{2}\Big(1 - \prod_j (1 - 2 q_{j,t})\Big), \qquad q_{j,t} = \Pr[\text{fault } j \text{ anticommutes with } S]
```

Faults that commute with S never appear in p_t. That is the blind spot, treated formally in section 5.

**Cost of the sentinel.** The symmetry value is free only when S is diagonal in a measurement basis already used by the task. Otherwise one extra basis group is needed, and its cost enters the cost model. TFIM with S = product of X is the half-free case: Z-basis shots give ZZ correlators but not the X parity.

### 4.3 E-detector on the stream

After calibration, a reference level μ_0 is fixed as an upper confidence bound on the mean of the stream (section 6). Because z_t lies in [0, 1], the centered increment is sub-Gaussian with variance proxy 1/4, giving the e-value and the Shiryaev-Roberts type statistic:

```latex
e_i(\lambda) = \exp\big(\lambda (z_i - \mu_0) - \lambda^2 / 8\big), \qquad R_t = \sum_{k=1}^{t} \sum_{j} w_j \prod_{i=k}^{t} e_i(\lambda_j), \qquad \tau = \inf\{t : R_t \ge \gamma\}
```

The weights w_j sum to 1 over a grid of bets λ_j. Under the pre-change class (mean at most μ_0), the expected time to a false alarm is at least γ, which is the ARL guarantee of e-detectors from Shin, Ramdas and Rinaldo. Shot counts S_t may depend on the past, because each increment is a supermartingale step given the past.

### 4.4 From violation to risk shift

Two layers connect the stream to task risk. The first is exact. Write the noisy state as a mixture of an in-sector part and an out-of-sector part with weight p_t. For any observable O:

```latex
\big|\mathrm{Tr}(O\rho_t) - \mathrm{Tr}(O\sigma_t^{\mathrm{in}})\big| \le 2\, p_t\, \|O\|_\infty
```

This bounds only the visible part of the drift. Errors that stay inside the sector are invisible and make up the rest. The second layer handles that remainder empirically. Let Δ_t be the risk shift since the last calibration. Assumption A2 says Δ_t ≤ h(ν_t − ν_k) for an unknown nondecreasing h. The plan estimates h by isotonic regression on probe pairs (violation level, measured risk shift). Probes come from the labeled validation stream, and from controlled noise amplification by inserting identity-equivalent gate pairs at scales 1, 3 and 5. A confidence-sequence margin κ_t on the residuals gives the link bound U_t^link = ĥ_t(ν̂_t − ν_k) + κ_t.

### 4.5 Risk certificate

The certificate adds a statistical term and a drift allowance:

```latex
U_t^{\mathrm{cert}} = U_t^{\mathrm{stat}}(\alpha_{\mathrm{stat}}) + U_t^{\mathrm{link}}(\alpha_{\mathrm{link}}), \qquad \alpha = \alpha_{\mathrm{stat}} + \alpha_{\mathrm{link}}
```

U^stat is an empirical-Bernstein confidence sequence on the labeled validation losses since the last calibration. The validation samples must be fresh and disjoint from any data used to update θ, which is a hard requirement of the design. The link term needs the stationarity of residuals described in section 10 as risk R3.

### 4.6 Recalibration rule and cost-optimal threshold

Three rules act in order.

1. **Certify and stop:** if U^cert is at most the target τ, stop spending and output the model with its certificate.
2. **Recalibrate:** if the e-detector alarms, or U^cert exceeds τ after the validation stream has grown, pay c_cal and start a new era.
3. **Abstain:** if the remaining budget cannot cover one recalibration plus the minimum validation cost, or if U^cert still exceeds τ right after recalibration, report that τ is uncertifiable.

The detector threshold γ trades false-alarm cost against detection delay. Using a per-epoch cost c_cal / γ for false alarms and the standard delay approximation ln γ / (2δ²) for a violation shift δ, with c_d the cost per epoch of running uncertified:

```latex
J(\gamma) = \frac{c_{\mathrm{cal}}}{\gamma} + c_d\,\frac{\ln \gamma}{2\delta^2} \quad\Rightarrow\quad \gamma^* = \frac{2\,\delta^2\, c_{\mathrm{cal}}}{c_d}
```

Here δ is the smallest violation shift that pushes the certificate past τ, obtained by inverting the link map. This is a first-order result; the paper validates it empirically and states its approximation error rather than proving a tight bound.

### 4.7 Sentinel library for the blind spot

A library of symmetries Σ = {S_1, ..., S_m} (for example both X-parity and Z-parity for TFIM) lets different symmetries see different faults. Choosing the cheapest subset that covers the fault families of interest is a set-cover problem, solved greedily with a (1 + ln m) approximation.

## 5. Theoretical contributions

Four results carry the paper, and only one of them (the visibility limit) is high in novelty. The others adapt known tools to a new setting, and the paper should say so.

| Result | Statement | Proof strategy | Novelty |
| --- | --- | --- | --- |
| T1 Detector validity | For the symmetry stream with predictable shot counts, the e-detector has expected false-alarm time at least γ, and detection delay of order ln γ divided by 2δ² | Supermartingale property of each increment; e-detector theory of Shin, Ramdas, Rinaldo | Low |
| T2 Visibility limit | For a circuit whose gates all commute with S and independent Pauli faults, the violation probability equals the closed form in section 4.2. Faults commuting with S add zero violation for any magnitude, yet can shift risk. A greedy sentinel library covers a chosen fault family within 1 + ln m of the minimum cost | Conjugation by gates that commute with S preserves commutation of each fault; parity of anticommuting faults; explicit counterexample channel; set-cover approximation | High |
| T3 Risk-link certificate | Under assumptions A1 to A4, the link bound holds with probability at least 1 − α_link, and the combined certificate holds with probability at least 1 − α | Leakage bound from section 4.4, isotonic fit with predictable updates, confidence sequence on residuals | Medium |
| T4 Cost-aware rule | The three-rule procedure has false-certification probability at most α, and the threshold γ* in section 4.6 is the first-order optimum of the stated cost model | Optional stopping on predictable stopping times; first-order expansion of delay and false-alarm cost | Medium |

### Assumptions the results rely on

- **A1 Symmetric circuit and input.** Every gate commutes with S and inputs lie in a known sector. Compilation to hardware gates must preserve this, which is checked in unit test 2.
- **A2 Monotone link.** Risk shift since calibration is bounded by a nondecreasing function of the change in violation level.
- **A3 Pauli faults.** Faults are independent and Pauli, enforced on hardware by randomized compiling or twirling, whose extra cost is reported.
- **A4 Fresh validation data.** Labeled validation samples are disjoint from training data and arrive after θ_t is fixed.
- **A5 Stationary residuals.** The residuals of the link fit are stationary within an era. This is the weakest assumption and the first to test (section 10, R3).

### Why T2 is the main contribution

T2 says exactly what symmetry-based monitoring can and cannot guarantee. A practitioner learns which fault families need a second sentinel before trusting the certificate. The explicit counterexample, a channel commuting with S that moves the risk while the violation stays at zero, makes the limit concrete and falsifiable on simulated and replayed hardware data.

## 6. Algorithm workflow

Each epoch checks the certificate, the budget, and the alarm in that order, and the loop restarts after every recalibration.

### Cold start (start of every era)

1. Calibrate the device and record the cost coefficients for shots, queue time, calibration and the extra basis group.
2. Run n_0 epochs at baseline shots S_0 to estimate the mean of the violation stream, and set μ_0 as its upper confidence bound.
3. Sweep controlled noise (folding scales 1, 3 and 5) to produce the first probe pairs for the link map.
4. Run the first validation batch to start the statistical confidence sequence.
5. Set γ from the cost-optimal formula in section 4.6, with a floor of 10.

### Per-epoch loop

Three checks run in order, each with its own outcome:

1. **Certificate check:** if U^cert ≤ τ, certify and stop.
2. **Budget check:** if the remaining budget cannot cover one recalibration plus minimum validation, abstain and report τ as uncertifiable.
3. **Alarm check:** if R_t ≥ γ, or U^cert > τ after the validation stream has grown, recalibrate and restart the era (back to cold start). Otherwise continue to the next epoch.

*(The published Docs version shows this as a diagram: "recalibration loop, 3 checks, 3 outcomes".)*

Abstention is tested before recalibration, so the plan never starts a recalibration that the budget cannot finish.

## 7. Experimental design

The experiments test each gate on three symmetry families, four drift regimes and six baselines, with 1000 seeds per regime. All thresholds in section 3 are fixed before any run.

### 7.1 Benchmarks

| ID | Task | Symmetry | Sentinel | Sizes |
| --- | --- | --- | --- | --- |
| B1 | Transverse-field Ising phase classification (ordered vs disordered) | Z2, S = product of X | X-parity (extra basis group for Z-basis tasks) | n = 8, 12, 16 |
| B2 | XXZ chain regime classification | U(1), total Z magnetization | Z-basis magnetization, free | n = 8, 12 |
| B3 | Cluster-state SPT vs trivial product states | Z2 x Z2, two parities | Two sentinels, which tests the blind-spot library | n = 8, 12 |

For n = 16, noise is simulated by stochastic Pauli trajectory sampling in Qiskit Aer, because full density matrices at that size are too large.

### 7.2 Drift regimes

- **D1 Ornstein-Uhlenbeck drift:** gate over-rotation angles and readout flip rates follow mean-reverting stochastic processes.
- **D2 Pink-noise drift:** 1/f^α flux-like drift in two-qubit gate error, with correlated readout shifts.
- **D3 Sudden jump:** a step increase in two-qubit error on a subset of qubits at t = T/2. D3-visible uses faults that anticommute with S. D3-blind uses faults that commute with S, which is the direct test of T2.
- **D4 Hardware replay:** hourly calibration histories (T1, T2, readout error, two-qubit gate error) from public or own IBM backend records, replayed through the simulator, plus one short live session. Check the current allowance on the IBM Quantum open plan before planning live runs.

### 7.3 Baselines

| Baseline | Drift sensor | Recalibration rule | Guarantee |
| --- | --- | --- | --- |
| Never recalibrate | None | None | None |
| Periodic | None | Every K epochs, K tuned | Naive split conformal |
| Threshold on raw sentinel | Symmetry violation | Fixed z-score cutoff | None |
| Extra-circuit sentinel | Light-cone sentinel TV distance (Q-RACE style) | Threshold | Concentration bound only |
| Observable e-detector | Pauli observables via shadows (eSCD style, reimplemented) | e-detector alarm | ARL |
| Oracle | Knows true change points | Recalibrates at change points | Lower bound on cost |
| SymSentinel (this plan) | Symmetry violation, sentinel library | e-detector with γ* and three rules | ARL plus certificate |

### 7.4 Metrics and ablations

- **Metrics:** certified-risk violation rate, empirical ARL, detection delay, total cost (shots, queue time, calibration), shots to first certificate, abstention correctness, sentinel overhead as a fraction of shots, and blind-spot recall.
- **Ablations:** remove the calibrated link and keep only the leakage bound; remove the second sentinel; fixed γ instead of γ*; no randomized compiling; readout-drift confound with and without the readout sentinel.
- **Statistics:** 1000 seeds per regime, confidence intervals on every rate, and an honest report of any gate that fails.

## 8. Software architecture and unit tests

The package `symsentinel` has five subpackages, six pre-registered unit tests, and fixed seeds so every figure in the paper reruns from one command.

| Subpackage | Responsibility |
| --- | --- |
| `symsentinel.symmetry` | Symmetry operator library, circuit commutation checker, sentinel measurement groups, greedy set-cover sentinel selector |
| `symsentinel.detect` | E-detectors, predictable bets, threshold calibration for a target ARL |
| `symsentinel.certify` | Empirical-Bernstein confidence sequences, isotonic link map, residual confidence sequence |
| `symsentinel.control` | Three-rule recalibration policy, cost model, threshold γ* |
| `symsentinel.sim` | Drift regimes D1 to D3, Pauli trajectory noise, replay of D4 calibration logs (hardware adapters through qiskit-ibm-runtime) |

### Pre-registered unit tests

1. **Closed form:** violation rate from simulated symmetric circuits with independent Pauli faults matches the formula in section 4.2 within 3 standard errors.
2. **Symmetry preserved by compilation:** after transpiling to hardware gates, the circuit still commutes with S (exact check for n up to 8).
3. **Null ARL:** on streams with mean at most μ_0, the empirical ARL lower confidence bound is at least γ.
4. **Predictable shots:** with shot counts that depend on the past, the mean of the e-values stays at most 1.
5. **Anytime coverage:** in drift-free eras, the statistical confidence sequence covers the true risk at every epoch in at least 1 − α of runs.
6. **Blind spot:** a channel commuting with S gives violation within noise of zero while risk shifts by more than a set margin.

### Reproducibility

Pin package versions, record every random seed, store raw drift traces and certificate logs, and archive the final release with a Zenodo DOI. Hardware runs record backend name, calibration snapshot time, and job IDs.

## 9. Ten-week gated timeline

The plan runs ten weeks from Monday 9 November 2026, with one gate every two weeks and the preprint at the end of week 9.

| Gate | Checks | Week |
| --- | --- | --- |
| G0 | RQ0: prior-art protocol and the six unit tests | 1 |
| G1 | RQ1: detector validity (false-alarm rate, delay) | 3 |
| G2 | RQ2: visibility limit and blind-spot example | 5 |
| G3 | RQ3: calibrated risk link under D1 to D3 | 7 |
| G4 | RQ4: cost saving at equal certified risk | 9 |
| Preprint | Code, DOI and arXiv posting | end of week 9 |
| Submission | Quantum | week 10 |

Writing starts in week 6 and runs in parallel with the cost work. If any gate is more than one week late, cut benchmark B3 first and then the live hardware session (section 10, R8).

*(The published Docs version shows this as a timeline graphic: "ten-week plan, 5 gates, preprint, submission".)*

## 10. Risks and fallbacks

The most likely failure is a weak link between symmetry violation and task risk (R2 and R3), and the plan keeps a publishable paper even then.

| ID | Risk | Trigger | Fallback |
| --- | --- | --- | --- |
| R1 | Someone publishes the same idea | G0 search or alert finds a close match | Post a preprint early; narrow the claim to the visibility limit (T2) and the cost-aware rule |
| R2 | Symmetry sees too little real noise | Blind-spot recall below 50% on D4 replay | Keep T2 as the headline, add the second sentinel, and report the limit honestly |
| R3 | Link residuals are not stationary, so T3 fails | Residual drift test fails in D1 or D2 | Weaken T3 to time-averaged exceedance control, as in online conformal methods, and say so in the abstract |
| R4 | Sentinel is not free for the task basis | Extra basis group costs more than 15% of shots | Report overhead per benchmark; restrict the claim to the free cases (B2, and the Z-basis part of B1) |
| R5 | Randomized compiling cost is too high | Overhead above 30% of shots | Test A3 on simulation only and state the assumption explicitly |
| R6 | Little or no hardware access | Allowance too small for a live run | Use D4 replay only and label hardware as future work |
| R7 | Cost saving misses the 25% gate | G4 result below threshold | Drop the cost claim, keep the detection and certificate results |
| R8 | Schedule slips | Any gate more than one week late | Cut benchmark B3 first, then the live hardware session |
| R9 | Readout drift mimics gate drift | Violation moves with no gate change | Add the readout-only sentinel and report both channels |

## 11. Publication strategy and portfolio fit

Post a preprint at the end of week 9, submit to Quantum first, and write the abstract around three claims that the data can either support or refute.

### Abstract claims

1. A symmetric circuit gives a drift sensor at low extra shot cost, with a false-alarm guarantee.
2. The sensor has a proven blind spot, and a small sentinel library covers a chosen fault family.
3. A cost-aware recalibration rule with a risk certificate lowers total cost at equal certified risk.

### Figure plan

1. Pipeline schematic: symmetric circuit, syndrome stream, e-detector, link map, three rules.
2. Visible vs invisible faults: violation rate against fault type, theory and simulation.
3. Detector behavior: ARL and detection delay against γ.
4. Certificate validity: violation rate across D1 to D3 against baselines.
5. Cost against certified risk for all baselines.
6. Hardware replay (D4) results and blind-spot recall.

### Submission path

- **Week 9:** preprint with code and DOI, to timestamp the claim. Optionally post a short note on the visibility limit (T2) after gate G2 to timestamp the most novel result.
- **Week 10:** submit to Quantum. If it is rejected as too narrow, retarget IEEE Transactions on Quantum Engineering or npj Quantum Information with the hardware results emphasized.
- **Optional:** a short statistics-venue version focused on T1, T3 and T4 if the quantum framing is not required.

### Portfolio fit

The martingale and conformal machinery comes from Paper 1. There is no overlap with the QEC decoder papers (Papers 2 and 3), the graph AML work, or the biology project. The equivariant Lindbladian plan can move to a later paper slot; it shares the conformal toolkit and the symmetry theme but no results.

## 12. Sources

All entries were found through web search on 8 November 2026 and judged from search excerpts, not full reads. Read each paper in full during week 1, since the novelty claim depends on it.

- [Universal sequential changepoint detection of quantum observables via classical shadows (eSCD)](https://arxiv.org/pdf/2602.11846)
- [Adaptive Quantum Conformal Prediction](https://arxiv.org/pdf/2511.18225)
- [Blind symmetry matching in quantum states with application to shot-count reduction](https://arxiv.org/pdf/2606.19196)
- [Noise mitigation of quantum observables via learning from Hamiltonian symmetry decays (GUESS)](https://arxiv.org/pdf/2603.13060)
- [Group-theoretic error mitigation enabled by classical shadows and symmetries](https://arxiv.org/abs/2310.03071v1)
- [Runtime calibration as state-trajectory feedback control in quantum-classical workflows](https://www.emergentmind.com/papers/2605.11860)
- [SPARTA: chi-squared calibrated, risk-controlled exploration-exploitation for variational quantum algorithms](https://arxiv.org/pdf/2511.19551)
- [Can you trust your shot budget? Benchmarking conformal risk control for variational quantum algorithms](https://neurips.cc/virtual/2026/173906)
- [Conditional validity of quantum event classifiers under collider systematics](https://arxiv.org/pdf/2609.02781)
- [Non-exchangeable conformal risk control](https://arxiv.org/pdf/2310.01262)
- [E-detectors: a nonparametric framework for sequential change detection](https://arxiv.org/pdf/2203.03532)
