#!/usr/bin/env python3
"""
Extract blocks that begin with '#filename: <PDF name>' and convert each to PDF via pandoc.
Supports BOTH:
  1) Fenced code blocks where #filename: is the first line inside the fence, and
  2) Unfenced sections that simply start with a '#filename:' line.

Usage:
    python3 md_blocks_to_pdf.py plan_blocks.md

Requirements:
    - pandoc
    - One of: xelatex | lualatex | pdflatex | wkhtmltopdf
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# Match fenced blocks like:
# ```text
# #filename: Name.pdf
# <content>
# ```
FENCED_RE = re.compile(
    r"```[^\n]*\n#filename:\s*(.+?)\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE
)

# Match UNFENCED blocks:
# #filename: Name.pdf
# <content... up to the next #filename: or EOF>
UNFENCED_RE = re.compile(
    r"(?mi)^[ \t]*#filename:\s*(.+?)\s*$([\s\S]*?)(?=^[ \t]*#filename:|\Z)"
)

def which(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def ensure(cmd: str, hint: str):
    if not which(cmd):
        sys.exit(f"ERROR: '{cmd}' not found. {hint}")

def pick_pdf_engine() -> tuple[str, bool]:
    """Return (engine, is_latex_engine). Preference: xelatex -> lualatex -> pdflatex -> wkhtmltopdf"""
    for e in ("xelatex", "lualatex", "pdflatex"):
        if which(e):
            return e, True
    if which("wkhtmltopdf"):
        return "wkhtmltopdf", False
    sys.exit("ERROR: No PDF engine found. Install xelatex (recommended) or wkhtmltopdf.")

def unique_path(base: pathlib.Path) -> pathlib.Path:
    """Avoid overwriting: adds -1, -2 ... if file exists."""
    if not base.exists():
        return base
    i = 1
    while True:
        candidate = base.with_name(f"{base.stem}-{i}{base.suffix}")
        if not candidate.exists():
            return candidate
        i += 1

def normalize_text(s: str) -> str:
    # Remove BOM and NBSPs that sometimes appear from copy/paste
    return s.replace("\ufeff", "").replace("\u00a0", " ")

def parse_blocks(text: str):
    """Yield (file_name, content) from either fenced or unfenced style."""
    blocks = []

    # Try fenced first
    for fname, body in FENCED_RE.findall(text):
        blocks.append((fname.strip(), body.strip()))

    if blocks:
        return blocks

    # Fallback to unfenced
    for fname, body in UNFENCED_RE.findall(text):
        blocks.append((fname.strip(), body.strip()))

    return blocks

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 md_blocks_to_pdf.py <markdown_file_with_blocks>")

    src_path = pathlib.Path(sys.argv[1])
    if not src_path.exists():
        sys.exit(f"ERROR: file not found: {src_path}")

    ensure("pandoc", "Install from https://pandoc.org/installing.html")
    engine, is_latex = pick_pdf_engine()

    text = normalize_text(src_path.read_text(encoding="utf-8"))
    blocks = parse_blocks(text)
    if not blocks:
        sys.exit("No blocks found. Expected either fenced blocks with '#filename:' as first line, "
                 "or unfenced sections starting with '#filename:'.")

    tmpdir = pathlib.Path(tempfile.mkdtemp())
    made = []

    for file_name, content in blocks:
        # Normalize to basename + .pdf
        out_pdf = pathlib.Path(file_name).with_suffix(".pdf").name
        out_pdf_path = unique_path(pathlib.Path.cwd() / out_pdf)

        md_tmp = tmpdir / (out_pdf_path.stem + ".md")
        md_tmp.write_text(content.strip() + "\n", encoding="utf-8")

        if is_latex:
            cmd = [
                "pandoc", str(md_tmp),
                "--from", "markdown+pipe_tables+grid_tables+table_captions+autolink_bare_uris",
                "--pdf-engine", engine,
                "-V", "fontsize=12pt",
                "-V", "geometry:margin=1in",
                "-o", str(out_pdf_path),
            ]
        else:
            cmd = [
                "pandoc", str(md_tmp),
                "-t", "html5", "-s",
                "--pdf-engine", engine,
                "-o", str(out_pdf_path),
            ]

        print("->", " ".join(cmd))
        subprocess.run(cmd, check=True)
        made.append(out_pdf_path)

    print("\nDone. Created:")
    for p in made:
        print("  ", p)

if __name__ == "__main__":
    main()


