import os
from chapters.ch1_introduction import append_ch1
from chapters.ch2_literature_review import append_ch2
from chapters.ch3_methodology import append_ch3
from chapters.ch4_implementation import append_ch4
from chapters.ch5_results import append_ch5
from chapters.ch6_discussion import append_ch6
from chapters.ch7_conclusion import append_ch7
from chapters.back_matter import append_back_matter

def append_all_chapters(story, styles, p, b, sp, make_box, caption_style, ref_style, fig_dir, tracker=None):
    """
    Appends all 7 dissertation chapters, references, and appendices to the ReportLab story.
    Supports dynamic page tracking for Table of Contents, List of Figures, and List of Tables.
    """
    append_ch1(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker)
    append_ch2(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker)
    append_ch3(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker)
    append_ch4(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker)
    append_ch5(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker)
    append_ch6(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker)
    append_ch7(story, styles, p, b, sp, make_box, caption_style, fig_dir, tracker)
    append_back_matter(story, styles, p, b, sp, make_box, caption_style, ref_style, tracker)
