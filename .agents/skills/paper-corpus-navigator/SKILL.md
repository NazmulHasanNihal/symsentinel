---
name: paper-corpus-navigator
description: Deep research navigation, full-text search, and theorem extraction across the 100 indexed SymSentinel research papers in ./papers/. Use when synthesizing prior art, extracting mathematical definitions, cross-referencing e-detector or conformal bounds, or inspecting experimental setups.
license: Apache-2.0
allowed-tools: Run Command, Read File, Write File
metadata:
  version: "1.0"
  skill-author: SymSentinel Core
---

# Paper Corpus Navigator

## When to Use
Use this skill to perform deep evidence synthesis, literature reviews, claim verification, and mathematical extraction across the 100 research papers stored in `papers/*.pdf` and indexed in `papers/.index/corpus_index.json`.

## Core CLI Tooling
The repository includes a dedicated full-text search engine: `scripts/search_papers.py`.

### 1. Keyword & Phrase Search
Search across all 100 papers for any concept, theorem name, or technique:
```bash
python scripts/search_papers.py "e-detector"
python scripts/search_papers.py "conformal risk control" --limit 10
python scripts/search_papers.py "classical shadows" --section 4
```

### 2. Search by Research Plan Section
Filter search results by the 7 SymSentinel pillars:
- `--section 1`: Sequential Testing & E-Processes (Ramdas, Grünwald, Vovk, Shafer)
- `--section 2`: Conformal Risk Control & Distribution Shift (Candès, Tibshirani, Angelopoulos)
- `--section 3`: Quantum Error Mitigation & Symmetry Verification (Temme, Endo, McArdle)
- `--section 4`: Measurement Frugality & Classical Shadows (Huang, Kueng, Preskill)
- `--section 5`: Geometric & Symmetry-Aware QML (Larocca, Cerezo, Meyer)
- `--section 6`: Hardware Drift & Calibration Dynamics (Blumoff, IBM Quantum, Google Quantum)
- `--section 7`: Quantum Sequential Testing & Shadow Change Detection (Zecchin, Simeone)

### 3. Inspect Specific Paper Details & Abstract
Look up metadata and the abstract for an exact arXiv ID:
```bash
python scripts/search_papers.py --id 2608.12660
```

### 4. High-Fidelity Markdown Extraction for LLM Analysis
Extract full structured Markdown (including formulas, headings, and tables) from any PDF using `pymupdf4llm`:
```bash
python scripts/search_papers.py --export-md 2608.12660
# Outputs clean Markdown to papers/2608.12660.md
```

## Deep Research Protocol
When answering research questions or verifying prior art:
1. **Find Exact Provenance**: Always cite the Ref (e.g. `1.19`), arXiv ID, and exact page number.
2. **Extract Definitions Before Claiming Gaps**:
   - For e-detectors: verify whether the paper assumes singleton nulls, composite nulls, or i.i.d. vs non-exchangeable processes.
   - For quantum drift: check if drift is modeled as unitary (Hamiltonian), Pauli, or general CPTP.
3. **Compare Claims with Table 2 of Research Plan**:
   - Check if any recent 2026 paper addresses both free symmetry sentinels and anytime-valid recalibration.

