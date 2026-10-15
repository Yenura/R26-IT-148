"""CORRECT div nesting trace using <div[ >] (not <div\b which matches </div>)."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
lines = path.read_text(encoding="utf-8").splitlines()

depth = 0
for i, line in enumerate(lines):
    s = re.sub(r'{/\*.*?\*/}', '', line)  # strip JSX comments
    opens = len(re.findall(r'<div[\s>]', s))   # <div followed by space or >
    closes = len(re.findall(r'</div>', s))
    old = depth
    depth += opens - closes
    # Show key structural lines and any line where depth goes negative
    if depth < 0 or (163 <= i+1 <= 170) or (209 <= i+1 <= 214) or (413 <= i+1 <= 422) or (612 <= i+1 <= 620) or (730 <= i+1 <= 738):
        print(f"L{i+1:3d} {old}->{depth} ({opens}o {closes}c) | {line.rstrip()[:90]}")

print(f"\nFinal depth: {depth}")
total_opens = sum(len(re.findall(r'<div[\s>]', re.sub(r'{/\*.*?\*/}', '', l))) for l in lines)
total_closes = sum(len(re.findall(r'</div>', l)) for l in lines)
print(f"Total: {total_opens} opens, {total_closes} closes, balance={total_opens-total_closes}")
