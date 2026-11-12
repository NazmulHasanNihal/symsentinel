---
name: symsentinel-research
description: Orchestrates and executes the SymSentinel research plan (Paper 4). Coordinates the 5 Research Gates (G0 to G4), anytime-valid recalibration rules, calibrated risk links, free symmetry sentinel verification, and cost-aware benchmarking. Use when planning research milestones, verifying gate thresholds, or implementing symsentinel package components.
license: Apache-2.0
allowed-tools: Run Command, Read File, Write File
metadata:
  version: "1.0"
  skill-author: SymSentinel Core
---

# SymSentinel Research & Gate Protocol

## When to Use
Use this skill to guide and audit research progress on SymSentinel (*Anytime-Valid Recalibration of Symmetric Quantum Learners from Free Symmetry Syndromes under Hardware Drift*). It enforces the pre-registered pass thresholds for Gates G0 through G4.

## Research Questions & Gates Matrix

| Gate | Research Question | Hypothesis | Pass Threshold | Target Week |
| :--- | :--- | :--- | :--- | :--- |
| **G0** | Is the gap real? | No published work combines free symmetry sentinel + anytime-valid detector + cost-aware recalibration + characterized blind spot | Fixed-protocol corpus search confirms novelty; all 6 unit tests pass | Week 1 |
| **G1** | Is the free-sentinel detector valid? | Predictable shot counts keep e-detector ARL at or above target | False-alarm rate $\le 1/500$ per epoch over 1,000 null runs; detection delay within $2\times$ of theory | Week 3 |
| **G2** | What can symmetry violation not see? | Noise covariant with symmetry gives zero violation yet shifts risk | Closed-form violation formula matches simulation within $3$ standard errors; blind-spot example confirmed | Week 5 |
| **G3** | Is the calibrated risk link valid? | Monotone map plus exceedance e-process bounds risk shift anytime | Violation rate $\le 0.05$ under drift regimes D1–D3; periodic baseline violates by $> 2\times$ | Week 7 |
| **G4** | Does it save cost? | Cost-aware threshold beats fixed schedules at equal certified risk | $\ge 25\%$ lower total cost (calibration + shots) than best periodic or threshold baseline | Week 9 |

## Core Research Protocol
1. **Never alter a pass threshold mid-experiment.** If a gate fails, execute the registered fallback in Section 10 of `SymSentinel_Research_Plan_v4.md`.
2. **Zero Extra Shot Cost Constraint:** The sentinel syndrome must be read from the **same** computational basis shots used for learning, with zero extra query overhead.
3. **Anytime Validity:** Every stopping rule must be an e-detector or test martingale with certified ARL control $\inf \mathbb{E}[T_b] \ge b$.

## Package Structure (`symsentinel`)
The planned open-source package layout:
```text
symsentinel/
├── __init__.py
├── sentinels/        # Z2, U(1), Z2xZ2 syndrome extraction from shot bitstrings
├── detectors/        # E-detectors, predictable mixture betting, stopping rules
├── risk/             # Calibrated risk monotone mapping and exceedance e-processes
├── drift/            # Drift simulation models (D1: unitary, D2: incoherent, D3: TLS jump)
└── benchmarks/       # Cost-aware benchmarks against periodic recalibration baselines
```

