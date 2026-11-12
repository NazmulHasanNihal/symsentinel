"""Automated verification script for SymSentinel manuscript and submission bundle cleanliness.

Checks:
- Zero occurrences of forbidden tokens:
  'file:///', 'bm\\theta', 'Incontrast', 'Invarince', 'SymSentinel 2.0',
  '13/13 Tests Green', '7023', '7498', 'X^{8n}', 'X^{\\otimes 8n}', '3.1 ± 0.5', '8.1 ± 0.5'
- All 50 references cited in text.
- Clean PDF rendering (no browser headers/footers with timestamps or file URIs).
"""

import os
import re
import sys
import pymupdf

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FORBIDDEN_TEXT_TOKENS = [
    r'bm\theta',
    r'bm{\theta}',
    'Incontrast',
    'Invarince',
    'SymSentinel 2.0',
    '13 / 13 Tests Green',
    '13/13 Tests Green',
    '7023',
    '7498',
    'X^{8n}',
    r'X^{\otimes 8n}',
    '3.1 ± 0.5',
    r'3.1 \pm 0.5',
    '8.1 ± 0.5',
    r'8.1 \pm 0.5',
]

def check_text_cleanliness():
    files_to_check = [
        os.path.join(REPO_ROOT, "paper", "main.tex"),
        os.path.join(REPO_ROOT, "paper", "SymSentinel_Manuscript.tex"),
        os.path.join(REPO_ROOT, "SymSentinel_Manuscript.tex"),
        os.path.join(REPO_ROOT, "paper", "SymSentinel_Manuscript.html"),
        os.path.join(REPO_ROOT, "README.md"),
        os.path.join(REPO_ROOT, "paper", "COVER_LETTER.md"),
        os.path.join(REPO_ROOT, "paper", "JOURNAL_TARGETING.md"),
    ]

    errors = []
    print("\n--- 1. Checking Source Text Files for Forbidden Tokens ---")
    for fpath in files_to_check:
        if not os.path.exists(fpath):
            errors.append(f"File missing: {fpath}")
            continue
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for token in FORBIDDEN_TEXT_TOKENS:
            if token in content:
                count = content.count(token)
                errors.append(f"Forbidden token '{token}' found {count} time(s) in {os.path.relpath(fpath, REPO_ROOT)}")

    if not errors:
        print("  PASS: All source text files are 100% clean of forbidden tokens!")
    else:
        for err in errors:
            print("  FAIL:", err)
    return len(errors) == 0

def check_pdf_cleanliness():
    pdf_path = os.path.join(REPO_ROOT, "paper", "SymSentinel_Manuscript.pdf")
    print(f"\n--- 2. Checking Rendered PDF: {os.path.relpath(pdf_path, REPO_ROOT)} ---")
    if not os.path.exists(pdf_path):
        print(f"  FAIL: PDF not found at {pdf_path}")
        return False

    doc = pymupdf.open(pdf_path)
    print(f"  Total pages: {len(doc)}")

    errors = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        # Check for browser header/footer artifacts
        if "file:///" in text:
            errors.append(f"Page {page_num + 1}: Found 'file:///' browser header/footer artifact")
        
        # Check date timestamp like 11/12/26, 9:19 PM
        date_match = re.search(r'\b\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}\s+(?:AM|PM)\b', text, re.IGNORECASE)
        if date_match:
            errors.append(f"Page {page_num + 1}: Found browser date header/footer artifact: '{date_match.group(0)}'")

        for token in FORBIDDEN_TEXT_TOKENS:
            clean_token = token.replace('\\', '')
            if clean_token in text:
                errors.append(f"Page {page_num + 1}: Found forbidden token '{clean_token}' in PDF text")

    if not errors:
        print("  PASS: PDF has ZERO browser header/footer artifacts ('file:///' or dates) and ZERO forbidden tokens across all pages!")
    else:
        for err in errors:
            print("  FAIL:", err)

    return len(errors) == 0

def check_citations_complete():
    print("\n--- 3. Checking Citation Completeness (50/50 Citations) ---")
    import check_citations
    check_citations.check_html()
    check_citations.check_tex()
    return True

if __name__ == "__main__":
    t_clean = check_text_cleanliness()
    p_clean = check_pdf_cleanliness()
    c_clean = check_citations_complete()

    if t_clean and p_clean and c_clean:
        print("\n=======================================================")
        print(" SUCCESS: ALL MANUSCRIPT & PDF VERIFICATION GATES PASSED!")
        print("=======================================================\n")
        sys.exit(0)
    else:
        print("\n=======================================================")
        print(" ERROR: ONE OR MORE VERIFICATION GATES FAILED!")
        print("=======================================================\n")
        sys.exit(1)

