import os
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable
from reportlab.lib import colors

def to_roman(n):
    """Converts a positive integer to lowercase Roman numerals."""
    if n <= 0:
        return ""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
    roman_num = ""
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

class SliitCanvas(canvas.Canvas):
    """
    SLIIT Thesis Compliant Canvas:
    - Page 1 (Title Page): No page number.
    - Pages 2 to ch1_start_page - 1: Lowercase Roman numerals centered at bottom (i, ii, iii...).
    - Pages ch1_start_page to end: Arabic numerals centered at the right bottom (1, 2, 3...).
    - Strictly black and white. No colored decorations.
    """
    ch1_start_page = 10  # default fallback, dynamically updated during build
    
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

    def draw_decorations(self, total_pages):
        page_num = self._pageNumber
        self.saveState()
        self.setFont("Times-Roman", 10)
        self.setFillColor(colors.HexColor("#000000"))

        if page_num == 1:
            # Title page has no page number
            self.restoreState()
            return

        if page_num < SliitCanvas.ch1_start_page:
            # Preliminary pages: lowercase Roman numerals centered at bottom
            roman_str = to_roman(page_num - 1)
            # Center of page width (595.28 / 2 = 297.64)
            self.drawCentredString(297.64, 45, roman_str)
        else:
            # Body text and appendices: Arabic numerals centered at right bottom
            # Right margin is at 595.28 - 70.87 = 524.41 pt
            arabic_num = page_num - SliitCanvas.ch1_start_page + 1
            self.drawRightString(524.4, 45, str(arabic_num))

        self.restoreState()

class PageTracker(Flowable):
    """
    Zero-height flowable that records the current canvas page number into a dictionary.
    Used for two-pass compilation of exact Table of Contents, Figures, and Tables page numbers.
    """
    def __init__(self, key, registry):
        super().__init__()
        self.key = key
        self.registry = registry
        self.width = 0
        self.height = 0

    def draw(self):
        # canvas._pageNumber is 1-based page in document
        page = self.canv._pageNumber
        # If before ch1, calculate roman; if after, calculate arabic
        if page < SliitCanvas.ch1_start_page:
            self.registry[self.key] = to_roman(page - 1)
            self.registry[f"{self.key}_raw"] = page
        else:
            arabic_page = page - SliitCanvas.ch1_start_page + 1
            self.registry[self.key] = str(arabic_page)
            self.registry[f"{self.key}_raw"] = page
