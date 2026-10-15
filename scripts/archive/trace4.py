"""Find exact unclosed div in Tab 1."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
lines = path.read_text(encoding="utf-8").splitlines()

depth = 0
for i in range(210, 420):  # Tab 1 section (0-indexed)
    line = lines[i]
    s = re.sub(r'{/\*.*?\*/}', '', line)
    opens = len(re.findall(r'<div\b', s))
    closes = len(re.findall(r'</div>', s))
    old = depth
    depth += opens - closes
    if opens > 0 or closes > 0:
        print(f"L{i+1:3d} depth {old}->{depth} ({opens}+ {closes}-) | {line.rstrip()[:90]}")

print(f"\nTab 1 net depth: {depth}")
