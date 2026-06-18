"""
Shared utilities, color constants, and common imports for all PDF renderers.
"""
import os
import sys
import subprocess
import shutil

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# ── Color palette ─────────────────────────────────────────────────────────────
TEXT_DARK  = colors.HexColor("#222222")
TEXT_MUTED = colors.HexColor("#444444")
LINE_COLOR = colors.HexColor("#111111")
LINK_COLOR = colors.HexColor("#0000EE")


def escape_latex(text):
    """Escape special LaTeX characters in a string."""
    if not isinstance(text, str):
        return text

    # Replace non-breaking spaces
    text = text.replace('\xa0', ' ')

    special_chars = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
        '\u201c': '``',
        '\u201d': "''",
        '\u2018': '`',
        '\u2019': "'",
        '\u2013': '--',
        '\u2014': '---',
    }

    result = []
    i = 0
    n = len(text)
    while i < n:
        char = text[i]
        if char == '\\':
            if i + 1 < n and text[i + 1] in special_chars:
                result.append('\\')
            else:
                result.append('\\textbackslash{}')
        elif char in special_chars:
            if result and result[-1] == '\\':
                result.append(char)
            else:
                result.append(special_chars[char])
        else:
            result.append(char)
        i += 1

    return "".join(result)


def run_pdflatex(tex_filename, pdf_dir, label="document", keep_tex=False):
    """
    Run pdflatex twice in pdf_dir and raise on failure.
    Cleans up auxiliary files afterwards.
    Returns True on success.
    """
    base_name = os.path.splitext(tex_filename)[0]
    try:
        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_filename],
                cwd=pdf_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode != 0:
                raise Exception(
                    f"pdflatex exited with code {result.returncode}.\n"
                    f"Stdout:\n{result.stdout}\nStderr:\n{result.stderr}"
                )
        print(f"Successfully compiled {label} via LaTeX.")
        return True
    finally:
        exts = ['.aux', '.log', '.out']
        if not keep_tex:
            exts.append('.tex')
        for ext in exts:
            tmp = os.path.join(pdf_dir, f"{base_name}{ext}")
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception as e:
                    print(f"Warning: Could not remove {tmp}: {e}", file=sys.stderr)
