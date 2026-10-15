"""Find the unclosed <div> in SkillGap.jsx by tracking nesting depth precisely."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
content = path.read_text(encoding="utf-8")
lines = content.splitlines()

depth = 0
max_depth_line = 0
for i, line in enumerate(lines):
    s = line
    # Skip JSX comments
    s_clean = re.sub(r'{/\*.*?\*/}', '', s)
    # Skip string literals in attributes (rough)
    
    # Count opening div tags
    opens = len(re.findall(r'<div\b', s_clean))
    closes = len(re.findall(r'</div>', s_clean))
    
    old = depth
    depth += opens - closes
    
    if depth < 0:
        print(f"L{i+1:3d} NEGATIVE depth {old}->{depth}: {line.rstrip()[:100]}")

print(f"\nFinal depth: {depth}")
print(f"Total opens: {sum(len(re.findall(r'<div\b', l)) for l in lines)}")
print(f"Total closes: {sum(len(re.findall(r'</div>', l)) for l in lines)}")

# Now find which section has the imbalance
sections = [
    ("Imports + Function start", 0, 166),
    ("Tab bar", 186, 210),
    ("Tab 1", 210, 420),
    ("Tab 2", 420, 617),
    ("Tab 3", 617, 736),
    ("Closing", 736, 738),
]
for name, start, end in sections:
    o = sum(len(re.findall(r'<div\b', l)) for l in lines[start:end])
    c = sum(len(re.findall(r'</div>', l)) for l in lines[start:end])
    print(f"{name} (L{start+1}-L{end}): {o} opens, {c} closes, balance={o-c}")
