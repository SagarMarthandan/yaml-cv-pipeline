"""
ATS Report renderer — LaTeX primary, ReportLab fallback.
Handles documents with type: ats_report
"""
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from .utils import TEXT_DARK, LINE_COLOR, escape_latex, run_pdflatex


# ── LaTeX renderer ────────────────────────────────────────────────────────────

def create_ats_report_pdf(data, output_path):
    """Compile ATS_Report.yaml to a clean PDF via LaTeX (fallback to ReportLab)."""
    print(f"Attempting to compile ATS Report via LaTeX: {output_path}")

    company  = escape_latex(data.get('company',  ''))
    position = escape_latex(data.get('position', ''))
    subtitle = f"{company} \\textemdash{{}} {position}" if company and position else (company or position)
    subtitle_tex = f"\\\\[4pt]{{\\large {subtitle}}}" if subtitle else ""

    # ── Score Matrix ──────────────────────────────────────────────────────────
    matrix = data.get('ats_score_matrix', {})
    cat_labels = {
        'keywords_and_terminology': 'Keywords \\& Terminology',
        'experience_relevance':      'Experience Relevance',
        'technical_skills':          'Technical Skills',
        'formatting_and_parse':      'Formatting \\& Parse',
        'soft_skills_and_language':  'Soft Skills \\& Language',
    }
    matrix_rows = []
    for key, label in cat_labels.items():
        if key in matrix:
            cat      = matrix[key]
            current  = cat.get('current_score', 0)
            max_s    = cat.get('max_score', 0)
            criteria = escape_latex(str(cat.get('evaluation_criteria', '')))
            matrix_rows.append(f"{label} & {current} & {max_s} & {criteria} \\\\")
    matrix_rows_tex = "\n".join(matrix_rows)
    total_score     = matrix.get('total_score', 0)
    score_color     = ('green!50!black' if total_score >= 85
                       else 'orange!80!black' if total_score >= 65
                       else 'red!70!black')

    # ── Detractors ────────────────────────────────────────────────────────────
    detractors     = data.get('core_score_detractors', [])
    detractors_tex = "\n".join([f"  \\item {escape_latex(str(d))}" for d in detractors])

    # ── Improvement Blueprint ─────────────────────────────────────────────────
    bp = data.get('improvement_blueprint', {})

    lang_confirm = escape_latex(str(bp.get('target_language_confirmation', '')))

    density     = bp.get('bullet_point_density_audit', [])
    density_tex = "\n".join([f"  \\item {escape_latex(str(d))}" for d in density])

    swap      = bp.get('project_swap_directive', {})
    rem_projs = swap.get('remove_projects', [])
    add_projs = swap.get('add_projects', [])
    vol_check = escape_latex(str(swap.get('volume_constraint_check', '')))
    rem_tex   = "\n".join([f"  \\item {escape_latex(str(p))}" for p in rem_projs])
    add_rows  = []
    for p in add_projs:
        if isinstance(p, dict):
            n = escape_latex(str(p.get('name', '')))
            j = escape_latex(str(p.get('justification', '')))
            add_rows.append(f"  \\item \\textbf{{{n}}} --- {j}")
        else:
            add_rows.append(f"  \\item {escape_latex(str(p))}")
    add_tex = "\n".join(add_rows)

    kw           = bp.get('keyword_inventory', {})
    hard_skills  = ", ".join([escape_latex(str(s)) for s in kw.get('hard_skills',  [])])
    methods      = ", ".join([escape_latex(str(s)) for s in kw.get('methodologies', [])])
    domain_terms = ", ".join([escape_latex(str(s)) for s in kw.get('domain_terms',  [])])

    tuning     = bp.get('technical_skills_tuning', {})
    add_skills = ", ".join([escape_latex(str(s)) for s in tuning.get('add',    [])])
    rem_skills = ", ".join([escape_latex(str(s)) for s in tuning.get('remove', [])])

    outcomes     = bp.get('quantified_outcomes', [])
    outcomes_tex = "\n".join([f"  \\item {escape_latex(str(o))}" for o in outcomes])

    cal       = bp.get('ats_threshold_calibration', {})
    meets     = cal.get('meets_target', False)
    meets_str = ("\\textcolor{green!50!black}{\\textbf{YES \\textemdash{} Target met}}"
                 if meets else
                 "\\textcolor{red!70!black}{\\textbf{NO \\textemdash{} Below threshold (85)}}")
    raw_remedy = cal.get('remedy_suggestions', '')
    if isinstance(raw_remedy, list) and raw_remedy and not meets:
        items_tex = "\n".join([f"  \\item {escape_latex(str(r))}" for r in raw_remedy])
        remedy_tex = f"\n\n\\textit{{Remedies:}}\n\\begin{{itemize}}[noitemsep,leftmargin=*]\n{items_tex}\n\\end{{itemize}}"
    elif raw_remedy and not meets:
        remedy_tex = f"\n\n\\textit{{Remedy:}} {escape_latex(str(raw_remedy))}"
    else:
        remedy_tex = ""

    # ── Post-Rewrite ATS Score ────────────────────────────────────────────────
    post = data.get('post_rewrite_ats_score') or {}
    post_matrix  = post.get('ats_score_matrix') or {}
    post_total   = post_matrix.get('total_score')
    post_delta   = post.get('score_delta')
    post_verdict = post.get('score_gate_verdict')
    post_gaps    = post.get('remaining_gaps') or []

    post_rows = []
    for key, label in cat_labels.items():
        if key in post_matrix:
            cat     = post_matrix[key]
            current = cat.get('current_score', 0)
            max_s   = cat.get('max_score', 0)
            if current is None:
                continue
            criteria = escape_latex(str(cat.get('evaluation_criteria', '')))
            post_rows.append(f"{label} & {current} & {max_s} & {criteria} \\\\")
    post_rows_tex = "\n".join(post_rows)

    if post_total is not None:
        post_score_color = ('green!50!black' if post_total >= 85
                            else 'orange!80!black' if post_total >= 65
                            else 'red!70!black')
        delta_str = ''
        if post_delta is not None:
            n = int(post_delta) if str(post_delta).lstrip('+-').isdigit() else post_delta
            sign = '+' if isinstance(n, int) and n > 0 else ''
            delta_str = f" ({sign}{n})"
        if post_verdict:
            vok = str(post_verdict).upper() == 'PROCEED'
            post_verdict_tex = ("\\textcolor{green!50!black}{\\textbf{PROCEED \\textemdash{} Target met}}"
                                if vok else
                                "\\textcolor{red!70!black}{\\textbf{HOLD \\textemdash{} Below threshold (85)}}")
        else:
            post_verdict_tex = ''
        post_gaps_tex = "\n".join([f"  \\item {escape_latex(str(g))}" for g in post_gaps])
        post_gaps_block = (
            f"\n\\subsection{{Remaining Gaps}}\n"
            f"\\begin{{itemize}}[noitemsep,leftmargin=*]\n{post_gaps_tex}\n\\end{{itemize}}"
        ) if post_gaps else ""
        post_section_tex = f"""
\\section{{Post-Rewrite ATS Score}}

\\vspace{{4pt}}
\\begin{{tabular}}{{p{{4.8cm}}rr p{{5.8cm}}}}
\\toprule
\\textbf{{Category}} & \\textbf{{Score}} & \\textbf{{Max}} & \\textbf{{Evaluation Criteria}} \\\\
\\midrule
{post_rows_tex}
\\midrule
\\textbf{{Total}} & \\textcolor{{{post_score_color}}}{{\\textbf{{{post_total}{delta_str}}}}} & \\textbf{{100}} & \\\\
\\bottomrule
\\end{{tabular}}

{post_verdict_tex}{post_gaps_block}
"""
    else:
        post_section_tex = ''

    # ── LaTeX document ────────────────────────────────────────────────────────
    tex_content = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[margin=0.75in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\usepackage{{booktabs}}
\\usepackage{{array}}
\\usepackage[table]{{xcolor}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\usepackage{{hyperref}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\setlength{{\\parskip}}{{4pt}}

\\titleformat{{\\section}}{{\\large\\bfseries\\uppercase}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing{{\\section}}{{0pt}}{{12pt}}{{6pt}}
\\titleformat{{\\subsection}}{{\\normalsize\\bfseries}}{{}}{{0em}}{{}}
\\titlespacing{{\\subsection}}{{0pt}}{{8pt}}{{3pt}}

\\hypersetup{{colorlinks=true,urlcolor=black,linkcolor=black}}

\\begin{{document}}

{{\\Huge\\bfseries ATS Analysis Report}}{subtitle_tex}

\\vspace{{8pt}}

\\section{{ATS Score Matrix}}

\\vspace{{4pt}}
\\begin{{tabular}}{{p{{4.8cm}}rr p{{5.8cm}}}}
\\toprule
\\textbf{{Category}} & \\textbf{{Score}} & \\textbf{{Max}} & \\textbf{{Evaluation Criteria}} \\\\
\\midrule
{matrix_rows_tex}
\\midrule
\\textbf{{Total}} & \\textcolor{{{score_color}}}{{\\textbf{{{total_score}}}}} & \\textbf{{100}} & \\\\
\\bottomrule
\\end{{tabular}}

\\section{{Core Score Detractors}}
\\begin{{itemize}}[noitemsep,leftmargin=*]
{detractors_tex}
\\end{{itemize}}

\\section{{Improvement Blueprint}}

\\subsection{{Target Language}}
{lang_confirm}

\\subsection{{Bullet Point Density Audit}}
\\begin{{itemize}}[noitemsep,leftmargin=*]
{density_tex}
\\end{{itemize}}

\\subsection{{Project Swap Directive}}
\\textbf{{Remove:}}
\\begin{{itemize}}[noitemsep,leftmargin=*]
{rem_tex}
\\end{{itemize}}
\\textbf{{Add:}}
\\begin{{itemize}}[noitemsep,leftmargin=*]
{add_tex}
\\end{{itemize}}
\\textit{{Volume check:}} {vol_check}

\\subsection{{Keyword Inventory}}
\\textbf{{Hard Skills:}} {hard_skills}

\\textbf{{Methodologies:}} {methods}

\\textbf{{Domain Terms:}} {domain_terms}

\\subsection{{Technical Skills Tuning}}
\\textbf{{Add:}} {add_skills}

\\textbf{{Remove:}} {rem_skills}

\\subsection{{Quantified Outcomes}}
\\begin{{itemize}}[noitemsep,leftmargin=*]
{outcomes_tex}
\\end{{itemize}}

\\subsection{{ATS Threshold Calibration}}
{meets_str}{remedy_tex}
{post_section_tex}
\\end{{document}}
"""

    pdf_dir      = os.path.dirname(os.path.abspath(output_path))
    base_name    = os.path.splitext(os.path.basename(output_path))[0]
    tex_filename = f"{base_name}.tex"

    with open(os.path.join(pdf_dir, tex_filename), 'w', encoding='utf-8') as f:
        f.write(tex_content)

    try:
        run_pdflatex(tex_filename, pdf_dir, label="ATS Report")
        print(f"Successfully compiled ATS Report via LaTeX: {output_path}")
    except Exception as e:
        print(f"Error compiling LaTeX: {e}", file=sys.stderr)
        print("Falling back to ReportLab compilation...", file=sys.stderr)
        _create_ats_report_pdf_reportlab(data, output_path)


# ── ReportLab fallback ────────────────────────────────────────────────────────

def _create_ats_report_pdf_reportlab(data, output_path):
    """ReportLab fallback renderer for ATS_Report.yaml."""
    margin = 0.75 * inch
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
    )
    printable_width = A4[0] - 2 * margin
    styles = getSampleStyleSheet()

    h1     = ParagraphStyle('ATSH1', parent=styles['Normal'], fontName='Helvetica-Bold',
                            fontSize=20, leading=24, spaceAfter=4)
    h2     = ParagraphStyle('ATSH2', parent=styles['Normal'], fontName='Helvetica-Bold',
                            fontSize=10.5, leading=13)
    h3     = ParagraphStyle('ATSH3', parent=styles['Normal'], fontName='Helvetica-Bold',
                            fontSize=9.5, leading=12, spaceAfter=2)
    body   = ParagraphStyle('ATSBody', parent=styles['Normal'], fontName='Helvetica',
                            fontSize=9, leading=12.5, textColor=TEXT_DARK)
    bullet = ParagraphStyle('ATSBullet', parent=styles['Normal'], fontName='Helvetica',
                            fontSize=9, leading=12.5, leftIndent=12, firstLineIndent=-8,
                            spaceAfter=2, textColor=TEXT_DARK)

    def section_header(title):
        t = Table([[Paragraph(f'<b>{title.upper()}</b>', h2)]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('LINEBELOW',     (0,0), (-1,-1), 0.5, LINE_COLOR),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING',   (0,0), (-1,-1), 0),
            ('RIGHTPADDING',  (0,0), (-1,-1), 0),
        ]))
        return t

    story = []

    company  = data.get('company',  '')
    position = data.get('position', '')
    subtitle = f"{company} \u2014 {position}" if company and position else (company or position)

    story.append(Paragraph('<b>ATS Analysis Report</b>', h1))
    if subtitle:
        story.append(Paragraph(subtitle, body))
    story.append(Spacer(1, 8))

    # Score Matrix
    story.append(section_header('ATS Score Matrix'))
    story.append(Spacer(1, 6))

    matrix = data.get('ats_score_matrix', {})
    cat_labels = {
        'keywords_and_terminology': 'Keywords & Terminology',
        'experience_relevance':      'Experience Relevance',
        'technical_skills':          'Technical Skills',
        'formatting_and_parse':      'Formatting & Parse',
        'soft_skills_and_language':  'Soft Skills & Language',
    }
    table_data = [[Paragraph('<b>Category</b>', h3), Paragraph('<b>Score</b>', h3),
                   Paragraph('<b>Max</b>', h3),      Paragraph('<b>Evaluation Criteria</b>', h3)]]
    for key, label in cat_labels.items():
        if key in matrix:
            cat     = matrix[key]
            current = cat.get('current_score', 0)
            max_s   = cat.get('max_score', 0)
            crit    = str(cat.get('evaluation_criteria', ''))
            table_data.append([Paragraph(label, body), Paragraph(str(current), body),
                                Paragraph(str(max_s), body), Paragraph(crit, body)])
    total_score = matrix.get('total_score', 0)
    score_color = ('#1a7a1a' if total_score >= 85
                   else '#b35900' if total_score >= 65
                   else '#a00000')
    table_data.append([Paragraph('<b>Total</b>', h3),
                       Paragraph(f'<b><font color="{score_color}">{total_score}</font></b>', h3),
                       Paragraph('<b>100</b>', h3), Paragraph('', body)])

    score_table = Table(table_data, colWidths=[140, 40, 35, 235])
    score_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('LINEBELOW',     (0,0), (-1,0), 0.5, LINE_COLOR),
        ('LINEABOVE',     (0,-1), (-1,-1), 0.5, LINE_COLOR),
        ('LINEBELOW',     (0,-1), (-1,-1), 0.5, LINE_COLOR),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING',   (0,0), (-1,-1), 4),
        ('RIGHTPADDING',  (0,0), (-1,-1), 4),
        ('TOPPADDING',    (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))

    # Core Score Detractors
    detractors = data.get('core_score_detractors', [])
    if detractors:
        story.append(section_header('Core Score Detractors'))
        story.append(Spacer(1, 4))
        for d in detractors:
            story.append(Paragraph(f'&bull;&nbsp;&nbsp;{d}', bullet))
        story.append(Spacer(1, 6))

    # Improvement Blueprint
    bp = data.get('improvement_blueprint', {})
    if bp:
        story.append(section_header('Improvement Blueprint'))
        story.append(Spacer(1, 4))

        def sub(title, text=None, items=None):
            story.append(Paragraph(f'<b>{title}</b>', h3))
            if text:
                story.append(Paragraph(str(text), body))
            if items:
                for item in items:
                    story.append(Paragraph(f'&bull;&nbsp;&nbsp;{item}', bullet))
            story.append(Spacer(1, 4))

        sub('Target Language', bp.get('target_language_confirmation', ''))
        sub('Bullet Point Density Audit', items=bp.get('bullet_point_density_audit', []))

        swap     = bp.get('project_swap_directive', {})
        rem_p    = swap.get('remove_projects', [])
        add_p    = swap.get('add_projects', [])
        vol      = swap.get('volume_constraint_check', '')
        add_strs = []
        for p in add_p:
            if isinstance(p, dict):
                add_strs.append(f"{p.get('name','')} \u2014 {p.get('justification','')}")
            else:
                add_strs.append(str(p))
        story.append(Paragraph('<b>Project Swap Directive</b>', h3))
        story.append(Paragraph('<i>Remove:</i>', body))
        for p in rem_p:
            story.append(Paragraph(f'&bull;&nbsp;&nbsp;{p}', bullet))
        story.append(Paragraph('<i>Add:</i>', body))
        for a in add_strs:
            story.append(Paragraph(f'&bull;&nbsp;&nbsp;{a}', bullet))
        if vol:
            story.append(Paragraph(f'<i>Volume check:</i> {vol}', body))
        story.append(Spacer(1, 4))

        kw = bp.get('keyword_inventory', {})
        story.append(Paragraph('<b>Keyword Inventory</b>', h3))
        for label, key in [('Hard Skills', 'hard_skills'),
                            ('Methodologies', 'methodologies'),
                            ('Domain Terms', 'domain_terms')]:
            vals = ', '.join(kw.get(key, []))
            if vals:
                story.append(Paragraph(f'<b>{label}:</b> {vals}', body))
        story.append(Spacer(1, 4))

        tuning = bp.get('technical_skills_tuning', {})
        story.append(Paragraph('<b>Technical Skills Tuning</b>', h3))
        adds = ', '.join(tuning.get('add', []))
        rems = ', '.join(tuning.get('remove', []))
        if adds: story.append(Paragraph(f'<b>Add:</b> {adds}', body))
        if rems: story.append(Paragraph(f'<b>Remove:</b> {rems}', body))
        story.append(Spacer(1, 4))

        sub('Quantified Outcomes', items=bp.get('quantified_outcomes', []))

        cal       = bp.get('ats_threshold_calibration', {})
        meets     = cal.get('meets_target', False)
        meets_txt = ('<font color="#1a7a1a"><b>YES \u2014 Target met</b></font>' if meets
                     else '<font color="#a00000"><b>NO \u2014 Below threshold (85)</b></font>')
        story.append(Paragraph('<b>ATS Threshold Calibration</b>', h3))
        story.append(Paragraph(meets_txt, body))
        raw_remedy = cal.get('remedy_suggestions', '')
        if isinstance(raw_remedy, list):
            for r in raw_remedy:
                story.append(Paragraph(f'&bull;&nbsp;&nbsp;{r}', bullet))
        elif raw_remedy:
            story.append(Paragraph(f'<i>Remedy:</i> {raw_remedy}', body))

    # ── Post-Rewrite ATS Score ────────────────────────────────────────────────
    post = data.get('post_rewrite_ats_score') or {}
    post_matrix  = post.get('ats_score_matrix') or {}
    post_total   = post_matrix.get('total_score')
    post_delta   = post.get('score_delta')
    post_verdict = post.get('score_gate_verdict')
    post_gaps    = post.get('remaining_gaps') or []

    if post_total is not None:
        story.append(Spacer(1, 10))
        story.append(section_header('Post-Rewrite ATS Score'))
        story.append(Spacer(1, 6))

        post_table_data = [
            [Paragraph('<b>Category</b>', h3), Paragraph('<b>Score</b>', h3),
             Paragraph('<b>Max</b>', h3),      Paragraph('<b>Evaluation Criteria</b>', h3)]
        ]
        for key, label in cat_labels.items():
            if key in post_matrix:
                cat     = post_matrix[key]
                current = cat.get('current_score')
                max_s   = cat.get('max_score', 0)
                if current is None:
                    continue
                crit = str(cat.get('evaluation_criteria', ''))
                post_table_data.append([
                    Paragraph(label, body), Paragraph(str(current), body),
                    Paragraph(str(max_s), body), Paragraph(crit, body)
                ])

        post_score_color = ('#1a7a1a' if post_total >= 85
                            else '#b35900' if post_total >= 65
                            else '#a00000')
        delta_str = ''
        if post_delta is not None:
            try:
                n = int(post_delta)
                delta_str = f' (+{n})' if n > 0 else f' ({n})'
            except (ValueError, TypeError):
                delta_str = f' ({post_delta})'
        post_table_data.append([
            Paragraph('<b>Total</b>', h3),
            Paragraph(f'<b><font color="{post_score_color}">{post_total}{delta_str}</font></b>', h3),
            Paragraph('<b>100</b>', h3), Paragraph('', body)
        ])

        post_tbl = Table(post_table_data, colWidths=[140, 40, 35, 235])
        post_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#f0f0f0')),
            ('LINEBELOW',     (0,0), (-1,0), 0.5, LINE_COLOR),
            ('LINEABOVE',     (0,-1), (-1,-1), 0.5, LINE_COLOR),
            ('LINEBELOW',     (0,-1), (-1,-1), 0.5, LINE_COLOR),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(post_tbl)
        story.append(Spacer(1, 8))

        if post_verdict:
            vok = str(post_verdict).upper() == 'PROCEED'
            vcolor = '#1a7a1a' if vok else '#a00000'
            vlabel = ('\u2713 PROCEED \u2014 Target met' if vok
                      else '\u26a0 HOLD \u2014 Still below 85')
            story.append(Paragraph(
                f'<b>Post-Rewrite Verdict:</b> <font color="{vcolor}"><b>{vlabel}</b></font>', body
            ))
            story.append(Spacer(1, 4))

        if post_gaps:
            story.append(Paragraph('<b>Remaining Gaps</b>', h3))
            for g in post_gaps:
                story.append(Paragraph(f'&bull;&nbsp;&nbsp;{g}', bullet))

    doc.build(story)
    print(f"Successfully compiled ATS Report via ReportLab: {output_path}")
