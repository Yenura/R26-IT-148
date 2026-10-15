import os
import sys
import PyPDF2
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4

# Add current directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from thesis_builder.styles import (
    get_thesis_styles, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM
)
from thesis_builder.canvas_helper import SliitCanvas, PageTracker
from thesis_builder.front_matter import append_front_matter
from thesis_builder.ch1_intro import append_ch1
from thesis_builder.ch2_lit_review import append_ch2
from thesis_builder.ch3_methodology import append_ch3
from thesis_builder.ch4_design import append_ch4
from thesis_builder.ch5_implementation import append_ch5
from thesis_builder.ch6_results import append_ch6
from thesis_builder.ch7_discussion import append_ch7
from thesis_builder.ch8_commercialisation import append_ch8
from thesis_builder.ch9_conclusion import append_ch9
from thesis_builder.back_matter import append_back_matter

FIG_DIR = os.path.join(CURRENT_DIR, "figures")
PDF_OUTPUT_PATH = os.path.join(CURRENT_DIR, "IT22089236_DRAFT.pdf")

def sanitize_flowables(flowables):
    for f in flowables:
        if hasattr(f, 'text') and isinstance(f.text, str):
            f.text = f.text.replace('\u2014', ' - ').replace('\u2013', '-')
        elif hasattr(f, '_cellvalues'):
            for row in f._cellvalues:
                for c in row:
                    if hasattr(c, 'text') and isinstance(c.text, str):
                        c.text = c.text.replace('\u2014', ' - ').replace('\u2013', '-')

def assemble_story(styles, page_dict, tracker):
    story = []
    # Front Matter (Title, Declaration, Abstract, Acknowledgements, TOC, LOF, LOT, Abbreviations)
    append_front_matter(story, styles, page_dict)

    # Chapters 1 to 9
    append_ch1(story, styles, FIG_DIR, tracker)
    append_ch2(story, styles, FIG_DIR, tracker)
    append_ch3(story, styles, FIG_DIR, tracker)
    append_ch4(story, styles, FIG_DIR, tracker)
    append_ch5(story, styles, FIG_DIR, tracker)
    append_ch6(story, styles, FIG_DIR, tracker)
    append_ch7(story, styles, FIG_DIR, tracker)
    append_ch8(story, styles, FIG_DIR, tracker)
    append_ch9(story, styles, FIG_DIR, tracker)

    # Back Matter (References, Glossary, Appendices)
    append_back_matter(story, styles, tracker)
    sanitize_flowables(story)
    return story

def build_pdf():
    styles = get_thesis_styles()
    temp_pdf = os.path.join(CURRENT_DIR, "temp_pass1.pdf")

    print("--- PASS 1: DETERMINING DYNAMIC PAGE NUMBERS ---")
    page_dict = {}
    
    doc1 = SimpleDocTemplate(
        temp_pdf,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )
    story1 = assemble_story(styles, page_dict, page_dict)
    doc1.build(story1, canvasmaker=SliitCanvas)

    # Determine starting page of Chapter 1
    ch1_raw = page_dict.get('ch1_raw', 10)
    SliitCanvas.ch1_start_page = ch1_raw
    print(f"Chapter 1 starts on raw page: {ch1_raw}")

    # Re-calculate display page numbers in page_dict
    for k, v in list(page_dict.items()):
        if k.endswith('_raw'):
            continue
        raw_val = page_dict.get(f"{k}_raw")
        if raw_val is not None:
            if raw_val < ch1_raw:
                from thesis_builder.canvas_helper import to_roman
                page_dict[k] = to_roman(raw_val - 1)
            else:
                page_dict[k] = str(raw_val - ch1_raw + 1)

    print("--- PASS 2: GENERATING FINAL DISSERTATION PDF ---")
    doc2 = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )
    story2 = assemble_story(styles, page_dict, None)
    doc2.build(story2, canvasmaker=SliitCanvas)

    if os.path.exists(temp_pdf):
        try:
            os.remove(temp_pdf)
        except Exception:
            pass

    reader = PyPDF2.PdfReader(PDF_OUTPUT_PATH)
    total_pages = len(reader.pages)
    print(f"==================================================")
    print(f"SUCCESS! Dissertation compiled to: {PDF_OUTPUT_PATH}")
    print(f"Total Page Count: {total_pages} pages.")
    print(f"==================================================")
    return total_pages

if __name__ == "__main__":
    build_pdf()
