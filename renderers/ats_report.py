"""
ATS Report renderer — ReportLab only (reportfallback mode).
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
    """Compile ATS_Report.yaml to a clean PDF via ReportLab directly (ReportLab fallback mode)."""
    print(f"Compiling ATS Report via ReportLab fallback mode (no LaTeX): {output_path}")
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
