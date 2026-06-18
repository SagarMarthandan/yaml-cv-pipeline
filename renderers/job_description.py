"""
Job description renderer — LaTeX primary, ReportLab fallback.
Handles documents with type: job_description
"""
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from .utils import TEXT_DARK, LINE_COLOR, escape_latex, run_pdflatex


# ── LaTeX renderer ────────────────────────────────────────────────────────────

def create_job_description_pdf(data, output_path):
    print(f"Attempting to compile Job Description via LaTeX: {output_path}")

    company  = escape_latex(data.get('company',  'Company'))
    position = escape_latex(data.get('position', 'Position'))

    sections = data.get('sections', [])
    sections_tex_parts = []
    for sec in sections:
        title   = escape_latex(str(sec.get('title', '')))
        content = sec.get('content', '')
        bullets = sec.get('bullets', [])

        sec_tex = f"\\section{{{title}}}\n"

        if content:
            if isinstance(content, list):
                sec_tex += "\n\n".join([escape_latex(str(p)) for p in content])
            else:
                sec_tex += escape_latex(str(content))
            sec_tex += "\n"

        if bullets:
            bullet_lines = "\n".join([f"  \\item {escape_latex(str(b))}" for b in bullets])
            sec_tex += f"\\begin{{itemize}}[noitemsep,leftmargin=*]\n{bullet_lines}\n\\end{{itemize}}\n"

        sections_tex_parts.append(sec_tex)

    body_tex = "\n".join(sections_tex_parts)

    tex_content = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[margin=0.8in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\usepackage{{hyperref}}
\\usepackage{{parskip}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

\\titleformat{{\\section}}{{\\normalsize\\bfseries}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing{{\\section}}{{0pt}}{{12pt}}{{5pt}}

\\hypersetup{{colorlinks=true,urlcolor=black,linkcolor=black}}

\\begin{{document}}

{{\\Large\\bfseries {company} \\textemdash{{}} {position}}}

\\vspace{{8pt}}

{body_tex}

\\end{{document}}
"""

    pdf_dir      = os.path.dirname(os.path.abspath(output_path))
    base_name    = os.path.splitext(os.path.basename(output_path))[0]
    tex_filename = f"{base_name}.tex"

    with open(os.path.join(pdf_dir, tex_filename), 'w', encoding='utf-8') as f:
        f.write(tex_content)

    try:
        run_pdflatex(tex_filename, pdf_dir, label="Job Description")
        print(f"Successfully compiled Job Description via LaTeX: {output_path}")
    except Exception as e:
        print(f"Error compiling LaTeX: {e}", file=sys.stderr)
        print("Falling back to ReportLab compilation...", file=sys.stderr)
        _create_job_description_pdf_reportlab(data, output_path)


# ── ReportLab fallback ────────────────────────────────────────────────────────

def _create_job_description_pdf_reportlab(data, output_path):
    margin = 0.8 * inch
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
    )
    printable_width = A4[0] - (2 * margin)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'JDTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=15, leading=19,
        textColor=colors.black, spaceAfter=15,
    )
    section_style = ParagraphStyle(
        'JDSectionTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.black,
    )
    body_style = ParagraphStyle(
        'JDBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14,
        textColor=TEXT_DARK, spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        'JDBullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14,
        leftIndent=15, firstLineIndent=-10, spaceAfter=3, textColor=TEXT_DARK,
    )

    story = []

    comp = data.get('company', 'Company')
    pos  = data.get('position', 'Position')
    story.append(Paragraph(f"<b>{comp} \u2014 {pos}</b>", title_style))

    for sec in data.get('sections', []):
        title   = sec.get('title', '')
        content = sec.get('content', '')
        bullets = sec.get('bullets', [])

        t = Table([[Paragraph(f"<b>{title}</b>", section_style)]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('LINEBELOW',     (0,0), (-1,-1), 0.5, LINE_COLOR),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING',   (0,0), (-1,-1), 0),
            ('RIGHTPADDING',  (0,0), (-1,-1), 0),
        ]))

        sec_block = [t, Spacer(1, 6)]

        if content:
            if isinstance(content, list):
                for p in content:
                    sec_block.append(Paragraph(p, body_style))
            else:
                sec_block.append(Paragraph(content, body_style))

        for b in bullets:
            sec_block.append(Paragraph(f"&bull;&nbsp;&nbsp;{b}", bullet_style))

        sec_block.append(Spacer(1, 10))
        story.append(KeepTogether(sec_block))

    doc.build(story)
    print(f"Successfully compiled Job Description via ReportLab: {output_path}")
