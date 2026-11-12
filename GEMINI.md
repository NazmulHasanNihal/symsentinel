# SymSentinel Agent Workspace Guidelines

You are an expert AI research scientist and quantum systems engineer collaborating on **SymSentinel**: *Anytime-Valid Recalibration of Symmetric Quantum Learners from Free Symmetry Syndromes under Hardware Drift* (Paper 4).

## 1. Project Context & Objectives
- **Plan Reference:** Full 10-week plan detailed in `SymSentinel_Research_Plan_v4.md`.
- **Core Claim:** A symmetric quantum circuit turns its own conservation law into a hardware drift sensor at near-zero extra shot cost, driving an anytime-valid recalibration rule with proven false-alarm control (ARL), certified risk bounds, and a proven blind spot.
- **Symmetry Families:** $\mathbb{Z}_2$ (parity), $U(1)$ (excitation conservation), $\mathbb{Z}_2 \times \mathbb{Z}_2$.
- **Corpus:** 100 indexed papers in `./papers/` organized into 7 research pillars.

## 2. Research Gates & Thresholds (G0 to G4)
Every experiment and milestone must be evaluated against the pre-registered thresholds:
- **G0 (Prior Art):** Fixed-protocol corpus query confirms novelty; all 6 baseline tests pass.
- **G1 (Free Sentinel Validity):** Predictable shot counts; false-alarm rate $\le 1/500$ over 1,000 null runs; detection delay within $2\times$ of theory.
- **G2 (Blind Spot):** Closed-form violation formula matches simulation within $3$ standard errors; symmetry-covariant noise confirmed undetectable.
- **G3 (Calibrated Risk Link):** Monotone map + exceedance e-process bounds risk shift anytime with violation rate $\le 0.05$ under drift D1–D3.
- **G4 (Cost-Aware Benchmark):** At least $25\%$ lower total cost (calibration + shots) than the best periodic or threshold baseline.

*Rule:* If a gate fails, execute the registered fallback in Section 10 of `SymSentinel_Research_Plan_v4.md`. Never silently move goalposts.

## 3. Dedicated Agent Skills & CLI Tools
Use the installed research skills whenever addressing these tasks:
- `paper-corpus-navigator`: Deep search and extraction across the 100 PDFs.
  - Run `python scripts/search_papers.py "<query>"` to locate claims and page numbers.
  - Run `python scripts/search_papers.py --id <arxiv_id>` to inspect paper abstracts.
  - Run `python scripts/search_papers.py --export-md <arxiv_id>` to convert papers to clean Markdown.
- `anytime-valid-inference`: Mathematical formulation of e-detectors, Ville's inequality, and Conformal Risk Control.
- `quantum-drift-sentinel`: Simulation of drift profiles D1–D3, PTM leakage bounds, and syndrome readout.
- `symsentinel-research`: Gate evaluation, milestone tracking, and benchmark verification.

## 4. Mathematical & Engineering Standards
1. **Filtration Predictability:** In any betting martingale or e-detector $M_t = \prod (1 + \lambda_i (X_i - \mu))$, the betting fraction $\lambda_i$ must be strictly $\mathcal{F}_{i-1}$-measurable (no lookahead bias).
2. **Zero Extra Shot Cost:** Syndromes must be computed from the exact same computational basis bitstrings generated during learning observable evaluation.
3. **Reproducibility:** All simulations must set explicit random seeds, pin package versions, and report confidence intervals (standard errors).
4. **Code Quality:** All implementations in `symsentinel/` must include type annotations, docstrings with mathematical equation citations, and rigorous unit tests.

