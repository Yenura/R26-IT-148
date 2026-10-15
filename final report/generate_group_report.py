"""
generate_group_report.py
========================
Generates the comprehensive, publication-grade SLIIT Final Group Dissertation
for Research Project Identifier: R26-IT-148.

Title: AI-Driven Recruitment Ecosystem for Intelligent Job Matching and Predictive Career Development
Group Members:
  - D. T. D. Perera (IT22089236) - Component 1 Lead
  - Dulnith K. D. (IT22094872) - Component 2 Lead
  - K. G. Savinda N. Perera (IT22027610) - Component 3 Lead
  - Yenura S. Karunanayaka (IT22306272) - Component 4 Lead

Target Page Count: Strictly between 30 and 40 pages (Target: ~35-36 pages).
"""

import os
import sys
import re
import shutil
import PyPDF2
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, HRFlowable, Preformatted
)
from reportlab.pdfgen import canvas

from group_chapters import (
    append_group_front_matter,
    append_group_ch1,
    append_group_ch2,
    append_group_ch3,
    append_group_ch4,
    append_group_ch5,
    append_group_ch6,
    append_group_ch7,
    append_group_ch8,
    append_group_back_matter,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, "figures")
PDF_OUTPUT_PATH = os.path.join(BASE_DIR, "R26-IT-148_DRAFT.pdf")
PDF_COPY_PATH = os.path.join(BASE_DIR, "Group_Report_DRAFT.pdf")

# ----------------------------------------------------------------------
# NumberedCanvas for Running Header & Footer
# ----------------------------------------------------------------------
class GroupNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        # Suppress header and footer on Title Page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#1A365D"))  # Deep Navy
        
        # Running Header
        self.drawString(54, 785, "RecruitAI — AI-Driven Recruitment Ecosystem & Predictive Career Development")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawRightString(541, 785, "Group Dissertation | R26-IT-148 | SLIIT")
        
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.6)
        self.line(54, 778, 541, 778)

        # Running Footer
        self.line(54, 45, 541, 45)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawString(54, 32, "Faculty of Computing | Department of Computer Science & Software Engineering | SLIIT")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 32, page_str)
        
        self.restoreState()

def clean_xml(text):
    """Escapes XML entities safely for ReportLab Paragraphs."""
    text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', text)
    text = re.sub(r'<(?=[0-9\s=])', '&lt;', text)
    text = re.sub(r'(?<=[0-9\s=])>', '&gt;', text)
    return text

def build_group_report(body_leading=13.4, spacer_scale=0.92, body_size=9.3, page_map=None):
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor("#1A365D")   # Deep SLIIT Navy
    SECONDARY = colors.HexColor("#2B6CB0") # Slate Blue
    ACCENT = colors.HexColor("#C53030")    # Crimson
    DARK_TEXT = colors.HexColor("#2D3748") # Charcoal
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER_COL = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=27,
        alignment=1, textColor=PRIMARY, spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, leading=15,
        alignment=1, textColor=SECONDARY, spaceAfter=18
    )

    ch_num_style = ParagraphStyle(
        'ChapterNumber', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=ACCENT, spaceBefore=10 * spacer_scale, spaceAfter=3 * spacer_scale, keepWithNext=True
    )

    ch_title_style = ParagraphStyle(
        'ChapterTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=16, leading=20,
        textColor=PRIMARY, spaceAfter=10 * spacer_scale, keepWithNext=True
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11.5, leading=14.5,
        textColor=PRIMARY, spaceBefore=9 * spacer_scale, spaceAfter=4 * spacer_scale, keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=13,
        textColor=SECONDARY, spaceBefore=7 * spacer_scale, spaceAfter=3 * spacer_scale, keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=body_size, leading=body_leading,
        textColor=DARK_TEXT, alignment=4, spaceAfter=5.5 * spacer_scale
    )

    body_bold = ParagraphStyle(
        'Body_Bold', parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=body_size - 0.2, leading=body_leading - 0.5,
        textColor=DARK_TEXT, leftIndent=12, firstLineIndent=-8, spaceAfter=3.5 * spacer_scale
    )

    caption_style = ParagraphStyle(
        'CaptionStyle', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=10.5,
        alignment=1, textColor=colors.HexColor("#4A5568"), spaceBefore=3, spaceAfter=6 * spacer_scale
    )

    code_pre_style = ParagraphStyle(
        'CodePreStyle', parent=styles['Normal'],
        fontName='Courier', fontSize=7.4, leading=9.4,
        textColor=colors.HexColor("#1A202C")
    )

    ref_style = ParagraphStyle(
        'RefStyle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=10.4,
        textColor=DARK_TEXT, leftIndent=16, firstLineIndent=-16, spaceAfter=4 * spacer_scale
    )

    styles.add(title_style)
    styles.add(subtitle_style)
    styles.add(ch_num_style)
    styles.add(ch_title_style)
    styles.add(h1_style)
    styles.add(h2_style)
    styles.add(body_style)
    styles.add(body_bold)
    styles.add(bullet_style)
    styles.add(caption_style)
    styles.add(code_pre_style)
    styles.add(ref_style)

    def p(text, style=body_style):
        return Paragraph(clean_xml(text), style)

    def b(text):
        return Paragraph(clean_xml(text), bullet_style)

    def sp(h=8):
        return Spacer(1, h * spacer_scale)

    def make_box(text, bg=LIGHT_BG, border=BORDER_COL):
        pf = Preformatted(text, code_pre_style)
        t = Table([[pf]], colWidths=[487])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 1, border),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 7),
            ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ]))
        return t

    story = []

    # Front Matter (Pages 1 to 7)
    append_group_front_matter(story, styles, p, b, sp, make_box, caption_style, FIG_DIR, page_map)

    # Chapters 1 to 8
    append_group_ch1(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)
    append_group_ch2(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)
    append_group_ch3(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)
    append_group_ch4(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)
    append_group_ch5(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)
    append_group_ch6(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)
    append_group_ch7(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)
    append_group_ch8(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)

    # Back Matter (References, Appendix A, Appendix B)
    append_group_back_matter(story, styles, p, b, sp, make_box, caption_style, FIG_DIR)

    # Build Document
    doc.build(story, canvasmaker=GroupNumberedCanvas)

def scan_pdf_pages(pdf_path):
    """Scans the generated PDF to map exact chapter, figure, and table page numbers."""
    reader = PyPDF2.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    page_map = {}

    chapter_patterns = {
        'ch1': r'CHAPTER 1',
        'ch2': r'CHAPTER 2',
        'ch3': r'CHAPTER 3',
        'ch4': r'CHAPTER 4',
        'ch5': r'CHAPTER 5',
        'ch6': r'CHAPTER 6',
        'ch7': r'CHAPTER 7',
        'ch8': r'CHAPTER 8',
        'ref': r'REFERENCES',
        'appA': r'APPENDIX A',
        'appB': r'APPENDIX B',
    }

    item_patterns = {
        'fig1_1': r'Figure 1\.1',
        'fig1_2': r'Figure 1\.2',
        'fig4_1': r'Figure 4\.1',
        'fig4_2': r'Figure 4\.2',
        'fig6_1': r'Figure 6\.1',
        'fig6_2': r'Figure 6\.2',
        'fig6_3': r'Figure 6\.3',
        'tab1_1': r'Table 1\.1',
        'tab2_1': r'Table 2\.1',
        'tab3_1': r'Table 3\.1',
        'tab5_1': r'Table 5\.1',
        'tab6_1': r'Table 6\.1',
        'tab6_2': r'Table 6\.2',
        'tab6_3': r'Table 6\.3',
        'tab7_1': r'Table 7\.1',
        'tabA_1': r'Table A\.1',
        'tabB_1': r'Table B\.1',
    }

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        text = page.extract_text() or ""

        # Skip front matter (pages 1 to 7) so that LOF and LOT entries do not trigger false positive page detections
        if page_num >= 8:
            for key, pat in chapter_patterns.items():
                if key not in page_map and re.search(pat, text):
                    page_map[key] = page_num

            for key, pat in item_patterns.items():
                if key not in page_map and re.search(pat, text):
                    page_map[key] = page_num

    print(f"Scanned {total_pages} pages. Discovered page mapping:")
    for k, v in sorted(page_map.items()):
        print(f"  {k}: page {v}")

    return page_map, total_pages

def main():
    print("=" * 65)
    print("STARTING SLIIT FINAL GROUP DISSERTATION BUILD (R26-IT-148)")
    print("=" * 65)

    # Pass 1: Build draft
    print("\n--- PASS 1: Initial Compilation ---")
    build_group_report(body_leading=13.4, spacer_scale=0.92, body_size=9.3)
    page_map, total_pages = scan_pdf_pages(PDF_OUTPUT_PATH)
    print(f"Pass 1 Total Page Count: {total_pages} pages.")

    # Pass 2: Calibrated compilation with exact page numbers
    print("\n--- PASS 2: Calibrated Compilation with Exact Page Numbers ---")
    build_group_report(body_leading=13.4, spacer_scale=0.92, body_size=9.3, page_map=page_map)
    final_page_map, final_total_pages = scan_pdf_pages(PDF_OUTPUT_PATH)
    print(f"Pass 2 Final Total Page Count: {final_total_pages} pages.")

    # Verify if within 30 to 40 pages
    if 30 <= final_total_pages <= 40:
        print(f"\nSUCCESS: Page count {final_total_pages} is strictly within target range [30, 40] pages!")
    else:
        print(f"\nWARNING: Page count {final_total_pages} is outside target [30, 40]. Tuning typography...")
        # Auto-tune if needed
        if final_total_pages < 30:
            build_group_report(body_leading=14.4, spacer_scale=1.05, body_size=9.6, page_map=final_page_map)
        elif final_total_pages > 40:
            build_group_report(body_leading=13.2, spacer_scale=0.90, body_size=9.2, page_map=final_page_map)
        _, final_total_pages = scan_pdf_pages(PDF_OUTPUT_PATH)
        print(f"Tuned Page Count: {final_total_pages} pages.")

    # Duplicate to Group_Report_DRAFT.pdf
    shutil.copyfile(PDF_OUTPUT_PATH, PDF_COPY_PATH)
    print(f"Copied final PDF to: {PDF_COPY_PATH}")
    print(f"Primary output located at: {PDF_OUTPUT_PATH}")
    print("=" * 65)

if __name__ == "__main__":
    main()
