#!/usr/bin/env python3
"""Download the SymSentinel reading list from arXiv, checking each title first.

Usage:  python3 download_papers.py      (run next to papers.csv; needs internet)
Output: ./papers/*.pdf and ./papers/report.txt

Rules:
- Every arXiv ID is looked up on arXiv and its real title is compared with the
  title in papers.csv.
- Rows marked "verified" are always downloaded; a large title difference is
  only noted in the report.
- Rows marked "memory" (IDs written from memory) are downloaded only when the
  arXiv title matches; otherwise they are skipped and listed in the report.
"""
import csv
import difflib
import glob
import html
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "papers.csv")
OUT_DIR = os.path.join(HERE, "papers")
API = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
HEADERS = {"User-Agent": "symsentinel-reading-list/1.0 (personal research use)"}
PAUSE = float(os.environ.get("ARXIV_PAUSE", "1.0"))  # seconds between requests


def norm(text):
    text = re.sub(r"\s+", " ", text.lower().replace("-", " "))
    return re.sub(r"[^a-z0-9 ]", "", text).strip()


def similarity(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def fetch(url, tries=3, timeout=60):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 404:
                raise
            if exc.code == 429:
                time.sleep(5.0 * (i + 1))
            else:
                time.sleep(PAUSE * (i + 1))
        except Exception as exc:  # network errors vary widely
            last = exc
            time.sleep(PAUSE * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def get_title_from_abs(aid):
    """Fetch title directly from the arXiv abstract page."""
    url = f"https://arxiv.org/abs/{aid}"
    try:
        data = fetch(url, tries=2, timeout=15)
        html_str = data.decode("utf-8", errors="ignore")
        m = re.search(r'<meta name="citation_title" content="([^"]+)"', html_str)
        if not m:
            m = re.search(
                r'<h1 class="title mathjax"><span class="descriptor">Title:</span>\s*(.*?)\s*</h1>',
                html_str,
                re.DOTALL,
            )
        if m:
            t = html.unescape(m.group(1).strip())
            return re.sub(r"\s+", " ", t).strip()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
    except Exception:
        pass
    return None


def arxiv_titles(ids):
    """Fetch titles for a list of arXiv IDs using abs page scraping with API fallback."""
    found = {}
    for aid in ids:
        t = get_title_from_abs(aid)
        if t:
            found[aid] = t
        time.sleep(0.1)
    return found


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    os.makedirs(OUT_DIR, exist_ok=True)
    total = len(rows)
    print(f"Starting download of {total} papers from {CSV_PATH} ...", flush=True)

    report, saved, skipped = [], 0, 0
    for idx, r in enumerate(rows, 1):
        aid, want, status = r["arxiv_id"], r["title"], r["status"]
        label = f'{r["ref"]} {aid}'

        # Check if already downloaded on disk
        existing = glob.glob(os.path.join(OUT_DIR, f"{aid}_*.pdf"))
        valid_existing = [p for p in existing if os.path.getsize(p) > 10_000]

        actual = get_title_from_abs(aid)
        if actual is None:
            # Fallback to export API if available
            try:
                query = urllib.parse.urlencode({"id_list": aid, "max_results": 1})
                root = ET.fromstring(fetch(f"{API}?{query}", tries=1, timeout=10))
                entry = root.find(ATOM + "entry")
                if entry is not None:
                    t = re.sub(r"\s+", " ", entry.findtext(ATOM + "title", "")).strip()
                    if t and t.lower() != "error":
                        actual = t
            except Exception:
                pass

        if actual is None:
            msg = f"SKIPPED  {label}: not found on arXiv (expected: {want})"
            print(f"[{idx}/{total}] {msg}", flush=True)
            report.append(msg)
            skipped += 1
            continue

        sim = similarity(want, actual)
        if status == "memory" and sim < 0.6:
            msg = f"SKIPPED  {label}: title mismatch. Expected '{want}', arXiv says '{actual}'"
            print(f"[{idx}/{total}] {msg}", flush=True)
            report.append(msg)
            skipped += 1
            continue

        slug = re.sub(r"[^a-z0-9]+", "_", actual.lower()).strip("_")[:60]
        path = os.path.join(OUT_DIR, f"{aid}_{slug}.pdf")

        if (os.path.exists(path) and os.path.getsize(path) > 10_000) or valid_existing:
            msg = f"EXISTS   {label}: {actual}"
            print(f"[{idx}/{total}] {msg}", flush=True)
            report.append(msg)
            saved += 1
            continue

        try:
            data = fetch(f"https://arxiv.org/pdf/{aid}")
        except RuntimeError as exc:
            msg = f"FAILED   {label}: {exc}"
            print(f"[{idx}/{total}] {msg}", flush=True)
            report.append(msg)
            skipped += 1
            continue

        if not data.startswith(b"%PDF"):
            msg = f"FAILED   {label}: response was not a PDF"
            print(f"[{idx}/{total}] {msg}", flush=True)
            report.append(msg)
            skipped += 1
            continue

        tmp_path = path + ".tmp"
        with open(tmp_path, "wb") as out:
            out.write(data)
        os.replace(tmp_path, path)

        note = "" if sim >= 0.5 else f" (title differs from list: '{want}')"
        msg = f"OK       {label}: {actual}{note}"
        print(f"[{idx}/{total}] {msg} ({len(data)} bytes)", flush=True)
        report.append(msg)
        saved += 1
        time.sleep(PAUSE)

    report_path = os.path.join(OUT_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    print(f"\nDone: {saved} saved or already present, {skipped} skipped. See {report_path}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
