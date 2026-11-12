#!/usr/bin/env python3
"""Build a fast, searchable text index for all downloaded papers in ./papers/.

Extracts full text and page numbers from all 100 PDFs using pymupdf,
associates them with metadata from papers.csv, and stores the index in
./papers/.index/corpus_index.json.
"""
import csv
import json
import os
import re
import time
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAPERS_DIR = os.path.join(ROOT, "papers")
CSV_PATH = os.path.join(ROOT, "papers.csv")
INDEX_DIR = os.path.join(PAPERS_DIR, ".index")
INDEX_PATH = os.path.join(INDEX_DIR, "corpus_index.json")


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)

    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        meta_rows = {r["arxiv_id"]: r for r in csv.DictReader(fh)}

    pdf_files = [f for f in os.listdir(PAPERS_DIR) if f.endswith(".pdf")]
    print(f"Indexing {len(pdf_files)} papers in {PAPERS_DIR} ...", flush=True)

    t0 = time.time()
    corpus = {}

    for idx, fname in enumerate(sorted(pdf_files), 1):
        fpath = os.path.join(PAPERS_DIR, fname)
        aid_match = re.match(r"^(\d{4}\.\d{4,5})_", fname)
        aid = aid_match.group(1) if aid_match else fname.split("_")[0]
        meta = meta_rows.get(aid, {})

        try:
            doc = pymupdf.open(fpath)
            num_pages = len(doc)
            pages_data = []
            full_text_list = []

            for pno in range(num_pages):
                page_text = doc[pno].get_text()
                cleaned = clean_text(page_text)
                if cleaned:
                    pages_data.append({"page": pno + 1, "text": cleaned})
                    full_text_list.append(cleaned)

            combined_text = " ".join(full_text_list)

            # Try extracting abstract from first 1-2 pages
            abstract = ""
            abs_match = re.search(r"\babstract\b[:\s]*(.*?)(?:\b(?:1\s+introduction|i\.\s+introduction|introduction)\b)", combined_text[:4000], re.IGNORECASE)
            if abs_match:
                abstract = abs_match.group(1).strip()[:1000]
            elif pages_data:
                abstract = pages_data[0]["text"][:600]

            corpus[aid] = {
                "arxiv_id": aid,
                "file_name": fname,
                "ref": meta.get("ref", ""),
                "section": meta.get("section", ""),
                "title": meta.get("title", ""),
                "status": meta.get("status", ""),
                "pages": num_pages,
                "file_size": os.path.getsize(fpath),
                "abstract": abstract,
                "pages_content": pages_data,
            }
            doc.close()
        except Exception as exc:
            print(f"Error indexing {fname}: {exc}", flush=True)

    with open(INDEX_PATH, "w", encoding="utf-8") as out:
        json.dump(corpus, out, ensure_ascii=False)

    dt = time.time() - t0
    index_size_mb = os.path.getsize(INDEX_PATH) / (1024 * 1024)
    print(f"Successfully indexed {len(corpus)} papers in {dt:.2f}s ({index_size_mb:.2f} MB index saved to {INDEX_PATH})", flush=True)


if __name__ == "__main__":
    build_index()

