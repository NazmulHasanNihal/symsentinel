#!/usr/bin/env python3
"""Search and navigate the 100 SymSentinel research papers.

Usage:
  python scripts/search_papers.py "e-detector"
  python scripts/search_papers.py "classical shadows" --section 4
  python scripts/search_papers.py --id 2608.12660
  python scripts/search_papers.py --export-md 2608.12660
  python scripts/search_papers.py --list-sections
"""
import argparse
import json
import os
import re
import sys
import pymupdf4llm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAPERS_DIR = os.path.join(ROOT, "papers")
INDEX_PATH = os.path.join(PAPERS_DIR, ".index", "corpus_index.json")

SECTIONS = {
    "1": "Sequential Testing & E-Processes (Ramdas, Grünwald, Vovk, Shafer)",
    "2": "Conformal Risk Control & Distribution Shift (Candès, Tibshirani, Angelopoulos)",
    "3": "Quantum Error Mitigation & Symmetry Verification (Temme, Endo, McArdle)",
    "4": "Measurement Frugality & Classical Shadows (Huang, Kueng, Preskill)",
    "5": "Geometric & Symmetry-Aware QML (Larocca, Cerezo, Meyer)",
    "6": "Hardware Drift & Calibration Dynamics (Blumoff, IBM Quantum, Google Quantum)",
    "7": "Quantum Sequential Testing & Shadow Change Detection (Zecchin, Simeone)",
}


def load_corpus():
    if not os.path.exists(INDEX_PATH):
        print(f"Index not found at {INDEX_PATH}. Please run: python scripts/index_papers.py")
        sys.exit(1)
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def search(query, section=None, max_results=5, snippet_len=200):
    corpus = load_corpus()
    terms = [t.lower() for t in query.split() if len(t) > 2]
    if not terms:
        terms = [query.lower()]

    results = []

    for aid, item in corpus.items():
        if section and str(item.get("section", "")) != str(section):
            continue

        score = 0
        matching_snippets = []

        # Check title and abstract
        title_lower = item["title"].lower()
        abs_lower = item.get("abstract", "").lower()

        for term in terms:
            if term in title_lower:
                score += 15
            if term in abs_lower:
                score += 5

        # Check pages content
        for pdata in item.get("pages_content", []):
            page_text = pdata["text"]
            p_lower = page_text.lower()
            page_hits = 0
            for term in terms:
                cnt = p_lower.count(term)
                if cnt > 0:
                    page_hits += cnt
                    score += cnt

            if page_hits > 0:
                # Find best snippet
                first_term = terms[0]
                idx = p_lower.find(first_term)
                if idx != -1:
                    start = max(0, idx - 60)
                    end = min(len(page_text), idx + snippet_len)
                    snip = page_text[start:end].replace("\n", " ").strip()
                    matching_snippets.append((pdata["page"], snip))

        if score > 0:
            results.append({
                "score": score,
                "arxiv_id": aid,
                "ref": item.get("ref", ""),
                "section": item.get("section", ""),
                "title": item["title"],
                "pages": item["pages"],
                "file_name": item["file_name"],
                "snippets": matching_snippets[:3]
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


def export_markdown(aid):
    corpus = load_corpus()
    if aid not in corpus:
        # Try matching by prefix or partial
        matches = [k for k in corpus if aid in k]
        if not matches:
            print(f"Paper {aid} not found in corpus.")
            return
        aid = matches[0]

    item = corpus[aid]
    pdf_path = os.path.join(PAPERS_DIR, item["file_name"])
    out_md = os.path.join(PAPERS_DIR, f"{aid}.md")
    print(f"Extracting {item['title']} to {out_md} ...", flush=True)
    md_text = pymupdf4llm.to_markdown(pdf_path)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"Saved {len(md_text)} characters of Markdown to {out_md}")


def show_paper(aid):
    corpus = load_corpus()
    if aid not in corpus:
        matches = [k for k in corpus if aid in k]
        if not matches:
            print(f"Paper {aid} not found.")
            return
        aid = matches[0]
    p = corpus[aid]
    print("=" * 80)
    print(f"Paper [{p['ref']}] {p['arxiv_id']}: {p['title']}")
    print(f"Section {p['section']}: {SECTIONS.get(str(p['section']), 'Unknown')}")
    print(f"File: {p['file_name']} ({p['pages']} pages)")
    print("=" * 80)
    print("\nAbstract:")
    print(p.get("abstract", "No abstract found.")[:1200])
    print("\n" + "=" * 80)


def list_sections():
    corpus = load_corpus()
    sec_counts = {}
    for item in corpus.values():
        s = str(item.get("section", "Other"))
        sec_counts[s] = sec_counts.get(s, 0) + 1

    print("SymSentinel 100-Paper Research Corpus Structure:")
    print("-" * 75)
    for s_id, s_name in sorted(SECTIONS.items()):
        cnt = sec_counts.get(s_id, 0)
        print(f"Section {s_id} ({cnt:2d} papers): {s_name}")
    print("-" * 75)


def main():
    parser = argparse.ArgumentParser(description="Search and query SymSentinel paper corpus.")
    parser.add_argument("query", nargs="?", help="Search query keywords or phrase")
    parser.add_argument("--section", "-s", help="Filter by section (1 to 7)")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--id", help="Show details and abstract of a specific arXiv ID")
    parser.add_argument("--export-md", help="Export a specific paper to clean Markdown")
    parser.add_argument("--list-sections", action="store_true", help="List all corpus sections and paper counts")

    args = parser.parse_args()

    if args.list_sections:
        list_sections()
        return

    if args.export_md:
        export_markdown(args.export_md)
        return

    if args.id:
        show_paper(args.id)
        return

    if not args.query:
        parser.print_help()
        return

    res = search(args.query, section=args.section, max_results=args.limit)
    if not res:
        print(f"No results found for query: '{args.query}'" + (f" in section {args.section}" if args.section else ""))
        return

    print(f"\nFound {len(res)} matching papers for query: '{args.query}'" + (f" (Section {args.section})" if args.section else "") + ":\n")
    for idx, r in enumerate(res, 1):
        print(f"[{idx}] Ref {r['ref']} | arXiv:{r['arxiv_id']} (Score: {r['score']}, {r['pages']} pages)")
        print(f"    Title:   {r['title']}")
        print(f"    Section: {r['section']} ({SECTIONS.get(str(r['section']), '')})")
        print(f"    PDF:     papers/{r['file_name']}")
        for pno, snip in r["snippets"]:
            print(f"    Page {pno}: ... {snip} ...")
        print("-" * 80)


if __name__ == "__main__":
    main()

