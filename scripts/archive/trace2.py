"""Precise JSX div nesting depth tracker."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
lines = path.read_text(encoding="utf-8").splitlines()

depth = 0
for i, line in enumerate(lines):
    s = line
    # Count <div ...> opens (but not </div> and not <div ... />)
    opens = len(re.findall(r'<div[\s>]', s))
    # Also count self-closing <div ... /> (unlikely but handle)
    self_close = len(re.findall(r'<div[^/]*/>', s))
    closes = len(re.findall(r'</div>', s))
    
    old = depth
    depth += opens - self_close - closes
    
    # Print problematic areas
    if depth < 0:
        print(f"L{i+1:3d} depth {old}->{depth} | {line.rstrip()[:90]}")
    elif i >= 410 and i <= 420:
        print(f"L{i+1:3d} depth {old}->{depth} | {line.rstrip()[:90]}")
    elif i >= 730:
        print(f"L{i+1:3d} depth {old}->{depth} | {line.rstrip()[:90]}")

print(f"\nFinal depth: {depth}")
