"""Trace JSX nesting depth to find the imbalance."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
content = path.read_text(encoding="utf-8")
lines = content.splitlines()

depth = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    # Count opening tags (self-closing don't count as depth change)
    # Simple heuristic: count <tag that isn't self-closing or closing
    opens = len(re.findall(r'<(?!/)(?!br)(?!hr)(?!img)(?!input)(?!Link)(?!EmptyState)(?!PageHeader)(?!StatCard)', stripped))
    # But we also need to handle self-closing tags like <PageHeader ... />
    # And conditional expressions don't change JSX depth
    # Let's just track div, span, button, a, h2, h3, h4, p, svg, g, text, line, rect
    # More accurate: count JSX element opens and closes
    
    # Simpler: count <div and </div> (most common)
    div_opens = len(re.findall(r'<div[\s/>]', stripped))
    div_closes = len(re.findall(r'</div>', stripped))
    
    old_depth = depth
    depth += div_opens - div_closes
    
    # Print lines around the problematic area or where depth goes negative
    if depth < 0 or (i >= 410 and i <= 425) or (i >= 730):
        print(f"L{i+1:3d} depth {old_depth}->{depth} ({div_opens}+ {div_closes}-) | {stripped[:80]}")
