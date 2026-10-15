import os
import sys
import shutil
import PyPDF2
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4

# Add current directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from group_builder.styles import (
    get_group_styles, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM
)
from group_builder.canvas_helper import GroupSliitCanvas, PageTracker, to_roman
from group_builder.front_matter import append_group_front_matter
from group_builder.ch1_intro import append_group_ch1
from group_builder.ch2_problem import append_group_ch2
from group_builder.ch3_solution import append_group_ch3
from group_builder.ch4_integration import append_group_ch4
from group_builder.ch5_execution import append_group_ch5
from group_builder.ch6_validation import append_group_ch6
from group_builder.ch7_commercialisation import append_group_ch7
from group_builder.ch8_conclusion import append_group_ch8
from group_builder.back_matter import append_group_back_matter

FIG_DIR = os.path.join(CURRENT_DIR, "figures")
PDF_OUTPUT_PATH = os.path.join(CURRENT_DIR, "Group_Report_DRAFT.pdf")
SECOND_OUTPUT_PATH = os.path.join(CURRENT_DIR, "R26-IT-148_DRAFT.pdf")

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
    append_group_front_matter(story, styles, page_dict, tracker)

    # Chapters 1 to 8
    append_group_ch1(story, styles, FIG_DIR, tracker)
    append_group_ch2(story, styles, FIG_DIR, tracker)
    append_group_ch3(story, styles, FIG_DIR, tracker)
    append_group_ch4(story, styles, FIG_DIR, tracker)
    append_group_ch5(story, styles, FIG_DIR, tracker)
    append_group_ch6(story, styles, FIG_DIR, tracker)
    append_group_ch7(story, styles, FIG_DIR, tracker)
    append_group_ch8(story, styles, FIG_DIR, tracker)

    # Back Matter (References, Appendix A, Appendix B, Appendix C)
    append_group_back_matter(story, styles, tracker)
    sanitize_flowables(story)
    return story

def build_pdf():
    styles = get_group_styles()
    temp_pdf = os.path.join(CURRENT_DIR, "temp_group_pass1.pdf")

    print("=================================================================")
    print("SLIIT GROUP THESIS COMPILER (RESEARCH PROJECT: R26-IT-148)")
    print("=================================================================")
    print("--- PASS 1: TRACKING DYNAMIC PAGE NUMBERS ---")
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
    doc1.build(story1, canvasmaker=GroupSliitCanvas)

    # Determine starting page of Chapter 1
    ch1_raw = page_dict.get('ch1_raw', 10)
    GroupSliitCanvas.ch1_start_page = ch1_raw
    print(f"Chapter 1 starts on raw page: {ch1_raw}")

    # Re-calculate display page numbers in page_dict
    for k, v in list(page_dict.items()):
        if k.endswith('_raw'):
            continue
        raw_val = page_dict.get(f"{k}_raw")
        if raw_val is not None:
            if raw_val < ch1_raw:
                page_dict[k] = to_roman(raw_val - 1)
            else:
                page_dict[k] = str(raw_val - ch1_raw + 1)

    print("--- PASS 2: GENERATING FINAL GROUP DISSERTATION PDF ---")
    doc2 = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )
    story2 = assemble_story(styles, page_dict, None)
    doc2.build(story2, canvasmaker=GroupSliitCanvas)

    if os.path.exists(temp_pdf):
        try:
            os.remove(temp_pdf)
        except Exception:
            pass

    # Copy to project draft name
    shutil.copyfile(PDF_OUTPUT_PATH, SECOND_OUTPUT_PATH)
    print(f"Group report successfully compiled to: {PDF_OUTPUT_PATH}")
    print(f"Duplicate copy created at: {SECOND_OUTPUT_PATH}")

    # Inspect total page count
    with open(PDF_OUTPUT_PATH, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        total_pages = len(reader.pages)
        print(f"\n>>> TOTAL DOCUMENT PAGE COUNT: {total_pages} PAGES <<<")
        if 80 <= total_pages <= 100:
            print(f">>> PAGE COUNT REQUIREMENT SATISFIED: {total_pages} is between 80 and 100 pages! <<<")
        else:
            print(f">>> WARNING: PAGE COUNT {total_pages} IS OUTSIDE 80-100 RANGE! <<<")

    return total_pages

if __name__ == "__main__":
    build_pdf()
