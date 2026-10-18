"""Find the EXACT unclosed div in Tab 1 by tracking depth line by line."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
lines = path.read_text(encoding="utf-8").splitlines()

depth = 0
for i in range(210, 420):
    line = lines[i]
    s = re.sub(r'{/\*.*?\*/}', '', line)
    opens = len(re.findall(r'<div\b', s))
    closes = len(re.findall(r'</div>', s))
    old = depth
    depth += opens - closes
    if opens > 0 or closes > 0:
        marker = " <== UNBALANCED" if opens != closes else ""
        print(f"L{i+1:3d} {old}->{depth} ({opens}o {closes}c){marker} | {line.rstrip()[:90]}")

print(f"\nFinal Tab 1 depth: {depth}")
