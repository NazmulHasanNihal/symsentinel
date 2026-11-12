"""Citation checker across HTML manuscript and LaTeX main.tex."""

import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_html():
    gen_script = os.path.join(REPO_ROOT, "scripts", "generate_submission_pdfs.py")
    with open(gen_script, "r", encoding="utf-8") as f:
        text = f.read()

    idx_start = text.find('<ol class="references">')
    idx_end = text.find('</ol>', idx_start) if idx_start != -1 else -1

    if idx_start == -1 or idx_end == -1:
        print("Could not find references block in generate_submission_pdfs.py")
        return

    # Strip out the references list itself so we only count in-text citations in body + appendices
    manuscript_text = text[:idx_start] + text[idx_end + len('</ol>'):]
    
    # Extract all bracket citations: [1], [1, 2], [1-5], [23-30], etc.
    cited = set()
    for m in re.finditer(r'\[(\d+[\d\s,–-]*)\]', manuscript_text):
        content = m.group(1)
        # handle ranges and commas
        for token in re.split(r'[,;]', content):
            token = token.strip()
            if '–' in token or '-' in token:
                parts = re.split(r'[–-]', token)
                if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                    for num in range(int(parts[0]), int(parts[1]) + 1):
                        cited.add(num)
            elif token.isdigit():
                cited.add(int(token))

    all_50 = set(range(1, 51))
    missing = sorted(list(all_50 - cited))
    print(f"HTML Body: {len(cited)} / 50 references cited.")
    if missing:
        print(f"Missing references in HTML: {missing}")
    else:
        print("SUCCESS: All 50 references cited in HTML body!")

def check_tex():
    tex_path = os.path.join(REPO_ROOT, "paper", "main.tex")
    with open(tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    bib_path = os.path.join(REPO_ROOT, "paper", "references.bib")
    with open(bib_path, "r", encoding="utf-8") as f:
        bib_text = f.read()

    bib_keys = re.findall(r'@\w+\{([^,]+),', bib_text)

    cited = set()
    for m in re.finditer(r'\\cite\{([^}]+)\}', text):
        for k in m.group(1).split(','):
            cited.add(k.strip())

    missing = [k for k in bib_keys if k not in cited]
    print(f"TeX Body: {len(cited)} keys cited out of {len(bib_keys)}.")
    if missing:
        print(f"Missing keys in main.tex ({len(missing)}): {missing}")
    else:
        print("SUCCESS: All bib keys cited in main.tex!")

if __name__ == "__main__":
    check_html()
    check_tex()
