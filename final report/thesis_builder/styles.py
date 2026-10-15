import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable, Preformatted, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT

# Page geometry in points
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 113.386   # 40 mm
MARGIN_BOTTOM = 113.386 # 40 mm
MARGIN_TOP = 70.866     # 25 mm
MARGIN_RIGHT = 70.866   # 25 mm
PRINTABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 411.023 pt

def clean_xml(text):
    """Escapes XML entities for ReportLab Paragraphs safely."""
    text = str(text).replace('\u2014', ' - ').replace('\u2013', '-')
    text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', text)
    text = re.sub(r'<(?=[0-9\s=])', '&lt;', text)
    text = re.sub(r'(?<=[0-9\s=])>', '&gt;', text)
    return text

def get_thesis_styles():
    styles = getSampleStyleSheet()
    
    # Strict Monochrome Colors
    COLOR_BLACK = colors.HexColor("#000000")
    COLOR_LIGHT_GRAY = colors.HexColor("#F0F0F0")

    # Cover Page Styles
    styles.add(ParagraphStyle(
        'CoverInstitution', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=13, leading=17,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'CoverDepartment', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=10, leading=14,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        'CoverMainTitle', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=14.5, leading=19,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        'CoverDegreeHeading', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=12, leading=16,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceAfter=16
    ))
    styles.add(ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=10.5, leading=14.5,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        'CoverSubmissionNote', parent=styles['Normal'],
        fontName='Times-Italic', fontSize=9.5, leading=13.5,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceAfter=12
    ))

    # SLIIT Headings Standards (Times New Roman)
    # Chapter heading: All Capital  -  14 Font size, Bold
    styles.add(ParagraphStyle(
        'ChapterHeading', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=14, leading=18,
        alignment=TA_LEFT, textColor=COLOR_BLACK, spaceBefore=12, spaceAfter=8,
        keepWithNext=True
    ))

    # Section heading: Title case  -  12 Font size, Bold
    styles.add(ParagraphStyle(
        'SectionHeading', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=12, leading=16,
        alignment=TA_LEFT, textColor=COLOR_BLACK, spaceBefore=10, spaceAfter=4,
        keepWithNext=True
    ))

    # Sub-section heading: Sentence case  -  12 Font size, Bold
    styles.add(ParagraphStyle(
        'SubSectionHeading', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=12, leading=15,
        alignment=TA_LEFT, textColor=COLOR_BLACK, spaceBefore=8, spaceAfter=3,
        keepWithNext=True
    ))

    # Body text: Sentence case  -  12 Font size, 1.5 line spacing (17.5 pt leading)
    styles.add(ParagraphStyle(
        'ThesisBody', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=12, leading=17.5,
        alignment=TA_JUSTIFY, textColor=COLOR_BLACK, spaceAfter=4.5
    ))

    styles.add(ParagraphStyle(
        'ThesisBodyBold', parent=styles['ThesisBody'],
        fontName='Times-Bold'
    ))

    styles.add(ParagraphStyle(
        'ThesisBullet', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=11.5, leading=16,
        alignment=TA_JUSTIFY, textColor=COLOR_BLACK,
        leftIndent=16, firstLineIndent=-10, spaceAfter=3.5
    ))

    # Captions
    styles.add(ParagraphStyle(
        'TableCaption', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=9.5, leading=12.5,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceBefore=6, spaceAfter=3,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'FigureCaption', parent=styles['Normal'],
        fontName='Times-Italic', fontSize=9.5, leading=12.5,
        alignment=TA_CENTER, textColor=COLOR_BLACK, spaceBefore=3, spaceAfter=8
    ))

    # Single Spaced Body (For abstract, table cells, blocks)
    styles.add(ParagraphStyle(
        'SingleBody', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=10.5, leading=13.5,
        alignment=TA_JUSTIFY, textColor=COLOR_BLACK, spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=8.5, leading=10.5,
        alignment=TA_LEFT, textColor=COLOR_BLACK
    ))
    styles.add(ParagraphStyle(
        'TableCellBold', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=8.5, leading=10.5,
        alignment=TA_LEFT, textColor=COLOR_BLACK
    ))
    styles.add(ParagraphStyle(
        'TableCellCenter', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=8.5, leading=10.5,
        alignment=TA_CENTER, textColor=COLOR_BLACK
    ))
    styles.add(ParagraphStyle(
        'TableCellCenterBold', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=8.5, leading=10.5,
        alignment=TA_CENTER, textColor=COLOR_BLACK
    ))

    # Code Preformatted Box
    styles.add(ParagraphStyle(
        'CodeStyle', parent=styles['Normal'],
        fontName='Courier', fontSize=7.2, leading=9.0,
        textColor=COLOR_BLACK
    ))

    # References
    styles.add(ParagraphStyle(
        'RefStyle', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=9.0, leading=11.5,
        alignment=TA_JUSTIFY, textColor=COLOR_BLACK,
        leftIndent=18, firstLineIndent=-18, spaceAfter=3.5
    ))

    return styles

def create_table_box(data, col_widths, styles, is_header=True):
    """Creates a clean black and white bordered table."""
    t = Table(data, colWidths=col_widths)
    ts = [
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#000000")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#000000")),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 3.5),
        ('RIGHTPADDING', (0,0), (-1,-1), 3.5),
    ]
    if is_header:
        ts.append(('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEAEA")))
    t.setStyle(TableStyle(ts))
    return t

def create_code_box(code_text, styles, width=PRINTABLE_WIDTH):
    """Creates a clean monochrome code snippet box."""
    pf = Preformatted(code_text, styles['CodeStyle'])
    t = Table([[pf]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#000000")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t
