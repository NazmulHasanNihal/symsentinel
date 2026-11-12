# Formal Submission Cover Letter to the Editors of *Quantum*

**To:**  
The Editorial Board  
***Quantum***: The Open Journal for Quantum Science  
`editorial-office@quantum-journal.org`

**From:**  
1. **Md. Nazmul** (Corresponding Author)  
   • Role: Lead Researcher, Conceptualization, Methodology & Software Architecture  
   • Email: `nazmulhas36@gmail.com`  
   • ORCID Identifier: [0009-0001-6115-7823](https://orcid.org/0009-0001-6115-7823) (Direct: https://orcid.org/0009-0001-6115-7823)  

2. **Musrat Jahan Gungun** (Co-Author)  
   • Role: Data Curation, Baseline Benchmarking, Validation & Statistical Testing  
   • Email: `gungunjahan84@gmail.com`  
   • ORCID Identifier: [0009-0006-4249-9198](https://orcid.org/0009-0006-4249-9198) (Direct: https://orcid.org/0009-0006-4249-9198)  

3. **Maheli Ahmed** (Co-Author & Faculty Supervisor)  
   • Role: Faculty Supervision, Resources, Formal Analysis & Model Governance  
   • Email: `maheli.ahmed.cse.cot@gmail.com`  
   • ORCID Identifier: [0000-0002-5183-7496](https://orcid.org/0000-0002-5183-7496) (Direct: https://orcid.org/0000-0002-5183-7496)  

**Affiliation:**  
Department of Computer Science and Engineering, College of Technology, National University, Gazipur, Bangladesh

**Date:** November 12, 2026  

**Subject:** Submission of Research Manuscript: *"Anytime-Valid Recalibration of Symmetric Quantum Learners from Free Symmetry Syndromes under Hardware Drift"*

---

Dear Editors of *Quantum*,

We are pleased to submit our original research manuscript entitled **"Anytime-Valid Recalibration of Symmetric Quantum Learners from Free Symmetry Syndromes under Hardware Drift"** for consideration as a Regular Research Article in ***Quantum***.

### Background and Core Scientific Motivation
Physical hardware drift—manifesting as telegraphic two-level system (TLS) defect frequency jumps, stochastic local-oscillator phase drift, and energy relaxation decays—presents a major bottleneck for quantum processing units (QPUs) deployed on commercial clouds. Current industry practice relies on rigid, periodic recalibration schedules (typically every 8 to 24 hours). This approach imposes an unacceptable economic and operational trilemma: on stable days, between 60% and 80% of calibration routines are completely redundant, burning substantial cloud budgets and idling research queues; conversely, when abrupt hardware jumps occur between calibrations, quantum learners run on degraded hardware for hours, silently corrupting variational gradients and inference accuracy. Meanwhile, existing drift-benchmarking proposals (such as spectator qubits or randomized benchmarking interspersal) require dedicated quantum circuits, consuming 25% to 50% extra quantum shots.

### Central Contributions & Breakthroughs
In this manuscript, we present **SymSentinel**, a framework that completely eliminates the shot overhead of quantum hardware monitoring while introducing rigorous mathematical guarantees:
1. **Zero Extra Quantum Shot Cost ("Free Sentinels"):** We prove that for any symmetric quantum learner ($[U(\theta), S] = 0$), the standard computational basis measurement bitstrings already gathered for task observable evaluation inherently carry hardware drift syndromes. These syndromes can be evaluated classically in microseconds at **zero additional quantum shot cost**.
2. **Filtration-Predictable Betting E-Detectors (Theorem 1):** We construct a sequential test martingale with strictly predictable betting fractions ($\lambda_t \in \mathcal{F}_{t-1}$). Applying Ville's maximal inequality, we prove that our detector guarantees a rigorous Average Run Length lower bound ($\text{ARL} \ge \gamma$) under the null hypothesis without Gaussian or asymptotic assumptions. Over 1,000 independent null simulation runs, our detector achieved **zero false alarms**.
3. **The Blind-Spot Visibility Limit Theorem (Theorem 2):** We prove a fundamental algebraic limit theorem: a single symmetry sentinel $S$ is strictly blind to noise channels whose Kraus operators commute with $S$ ($[E_k, S] = 0$), even when task prediction risk degrades severely. We demonstrate this counterexample analytically and empirically, and provide a greedy set-cover algorithm over a sentinel library that restores **100% full Pauli fault visibility** with just $M=2$ sentinels.
4. **Anytime-Valid Conformal Risk Certification (Theorem 3):** Combining an empirical-Bernstein confidence sequence on validation data with an isotonic regression link map, we construct a time-uniform risk certificate $U_t^{\text{cert}}$ that upper bounds downstream task loss under non-stationary drift with certified miscoverage probability $\le \alpha$. Over 300 non-stationary drift trajectories (coherent Ornstein-Uhlenbeck phase drift, incoherent $T_1/T_2$ decay, and TLS jumps), SymSentinel maintained a **0.0% violation rate**.
5. **Three-Tier Recalibration Hierarchy & 96.6% Cloud Cost Reduction (Theorem 4):** Rather than triggering an expensive, monolithic \$100 full QPU reset upon every alarm, SymSentinel deploys a 3-tier cascade: software Virtual-$Z$ phase updates (\$0, 0 shots) $\to$ localized 2-qubit subsystem retuning (\$15, 1.5k shots) $\to$ full QPU reset. In comprehensive benchmarking across 6 baselines, SymSentinel achieves a **96.6% cost reduction compared to standard periodic recalibration and an 82.9% reduction compared to an omniscient oracle reset**.

### Fit for *Quantum*
This manuscript brings together mathematical quantum information theory, sequential anytime-valid statistics (e-processes and Ville bounds), and practical quantum computing systems. Given *Quantum*’s high standards for mathematical rigor, open science, and practical impact on quantum technologies, we believe our work will be of immediate interest to *Quantum*’s broad readership.

### Reproducibility & Open Science Commitments
In alignment with the editorial policies of *Quantum*:
- All source code is openly released as a documented, tested Python package (`symsentinel`) licensed under Apache-2.0.
- All unit tests (covering Gates G0 to G4) execute via standard `pytest` and pass with 100% green status.
- All raw experimental benchmark data are provided as structured JSON files.
- The manuscript is accompanied by 6 high-resolution publication figures (300 DPI) and full mathematical proofs in the Appendix.

### Suggested Handling Editors
- **Dr. Johannes Jakob Meyer** (*Freie Universität Berlin*) — Symmetry, representation theory, and geometric quantum machine learning.
- **Dr. Robin Blume-Kohout** (*Sandia National Laboratories*) — Quantum characterization, verification, and hardware drift benchmarking.
- **Dr. Earl Campbell** (*Riverlane / University of Sheffield*) — Quantum error mitigation and quantum systems engineering.

### Suggested Independent Reviewers
1. **Prof. Aaditya Ramdas** (*Carnegie Mellon University*, `aramdas@cmu.edu`): Expert in anytime-valid sequential inference, test martingales, and conformal risk control.
2. **Dr. Kenneth Proctor** (*Sandia National Laboratories*, `kprocto@sandia.gov`): Leading researcher on spectator qubits and quantum hardware drift characterization.
3. **Dr. Bálint Koczor** (*University of Oxford*, `balint.koczor@materials.ox.ac.uk`): Authority on symmetry verification and quantum error mitigation.
4. **Dr. Zoë Holmes** (*EPFL*, `zoe.holmes@epfl.ch`): Expert on variational quantum algorithms, equivariant architectures, and barren plateaus.

### Declarations
We confirm that this manuscript is original, has not been published previously, and is not currently under consideration for publication elsewhere. All authors have reviewed and approved the submission.

Thank you very much for your time and consideration of our work.

Sincerely,

**Md. Nazmul**  
Lead Researcher & Corresponding Author  
Department of Computer Science and Engineering, College of Technology,  
National University, Gazipur, Bangladesh  
ORCID: 0009-0001-6115-7823 | Email: `nazmulhas36@gmail.com`  
*(On behalf of Musrat Jahan Gungun and Maheli Ahmed)*

