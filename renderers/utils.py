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


_GOOGLE_SANS_CODE_REGISTERED = None

def register_google_sans_code():
    """
    Registers Google Sans Code TTF fonts with ReportLab.
    Looks in LOCALAPPDATA/Microsoft/Windows/Fonts and C:/Windows/Fonts.
    Returns (F_REG, F_BOLD, F_ITALIC, F_BOLDITALIC) representing the registered font names,
    or falls back to ('Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique') if not found.
    """
    global _GOOGLE_SANS_CODE_REGISTERED
    if _GOOGLE_SANS_CODE_REGISTERED is not None:
        return _GOOGLE_SANS_CODE_REGISTERED

    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        dirs = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
            r"C:\Windows\Fonts"
        ]
        
        regular_file = "GoogleSansCode-Regular.ttf"
        bold_file = "GoogleSansCode-Bold.ttf"
        italic_file = "GoogleSansCode-Italic.ttf"
        bold_italic_file = "GoogleSansCode-BoldItalic.ttf"

        regular_path = None
        bold_path = None
        italic_path = None
        bold_italic_path = None

        for d in dirs:
            if not d or not os.path.exists(d):
                continue
            r_p = os.path.join(d, regular_file)
            b_p = os.path.join(d, bold_file)
            i_p = os.path.join(d, italic_file)
            bi_p = os.path.join(d, bold_italic_file)
            
            if os.path.exists(r_p) and os.path.exists(b_p):
                regular_path = r_p
                bold_path = b_p
                if os.path.exists(i_p):
                    italic_path = i_p
                if os.path.exists(bi_p):
                    bold_italic_path = bi_p
                break

        if not regular_path or not bold_path:
            _GOOGLE_SANS_CODE_REGISTERED = ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique")
            return _GOOGLE_SANS_CODE_REGISTERED

        pdfmetrics.registerFont(TTFont("GoogleSansCode", regular_path))
        pdfmetrics.registerFont(TTFont("GoogleSansCode-Bold", bold_path))
        pdfmetrics.registerFont(TTFont("GoogleSansCode-Italic", italic_path if italic_path else regular_path))
        pdfmetrics.registerFont(TTFont("GoogleSansCode-BoldItalic", bold_italic_path if bold_italic_path else bold_path))
        
        pdfmetrics.registerFontFamily(
            "GoogleSansCode",
            normal="GoogleSansCode",
            bold="GoogleSansCode-Bold",
            italic="GoogleSansCode-Italic",
            boldItalic="GoogleSansCode-BoldItalic",
        )
        _GOOGLE_SANS_CODE_REGISTERED = ("GoogleSansCode", "GoogleSansCode-Bold", "GoogleSansCode-Italic", "GoogleSansCode-BoldItalic")
        return _GOOGLE_SANS_CODE_REGISTERED
    except Exception as e:
        print(f"Warning: Could not register Google Sans Code: {e}", file=sys.stderr)
        _GOOGLE_SANS_CODE_REGISTERED = ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique")
        return _GOOGLE_SANS_CODE_REGISTERED


_LM_ROMAN_10_REGISTERED = None

def register_lm_roman_10():
    """
    Registers LM Roman 10 TTF fonts with ReportLab.
    Looks in LOCALAPPDATA/Microsoft/Windows/Fonts and C:/Windows/Fonts.
    Returns (F_REG, F_BOLD, F_ITALIC, F_BOLDITALIC) representing the registered font names,
    or falls back to ('Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic') if not found.
    """
    global _LM_ROMAN_10_REGISTERED
    if _LM_ROMAN_10_REGISTERED is not None:
        return _LM_ROMAN_10_REGISTERED

    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        dirs = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
            r"C:\Windows\Fonts"
        ]
        
        regular_file = "lmroman10-regular.ttf"
        bold_file = "lmroman10-bold.ttf"
        italic_file = "lmroman10-italic.ttf"
        bold_italic_file = "lmroman10-bolditalic.ttf"

        regular_path = None
        bold_path = None
        italic_path = None
        bold_italic_path = None

        for d in dirs:
            if not d or not os.path.exists(d):
                continue
            r_p = os.path.join(d, regular_file)
            b_p = os.path.join(d, bold_file)
            i_p = os.path.join(d, italic_file)
            bi_p = os.path.join(d, bold_italic_file)
            
            if os.path.exists(r_p) and os.path.exists(b_p):
                regular_path = r_p
                bold_path = b_p
                if os.path.exists(i_p):
                    italic_path = i_p
                if os.path.exists(bi_p):
                    bold_italic_path = bi_p
                break

        if not regular_path or not bold_path:
            _LM_ROMAN_10_REGISTERED = ("Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic")
            return _LM_ROMAN_10_REGISTERED

        pdfmetrics.registerFont(TTFont("LMRoman10", regular_path))
        pdfmetrics.registerFont(TTFont("LMRoman10-Bold", bold_path))
        pdfmetrics.registerFont(TTFont("LMRoman10-Italic", italic_path if italic_path else regular_path))
        pdfmetrics.registerFont(TTFont("LMRoman10-BoldItalic", bold_italic_path if bold_italic_path else bold_path))
        
        pdfmetrics.registerFontFamily(
            "LMRoman10",
            normal="LMRoman10",
            bold="LMRoman10-Bold",
            italic="LMRoman10-Italic",
            boldItalic="LMRoman10-BoldItalic",
        )
        _LM_ROMAN_10_REGISTERED = ("LMRoman10", "LMRoman10-Bold", "LMRoman10-Italic", "LMRoman10-BoldItalic")
        return _LM_ROMAN_10_REGISTERED
    except Exception as e:
        print(f"Warning: Could not register LM Roman 10: {e}", file=sys.stderr)
        _LM_ROMAN_10_REGISTERED = ("Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic")
        return _LM_ROMAN_10_REGISTERED
