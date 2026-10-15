"""Check for JSX issues in SkillGap.jsx."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
content = path.read_text(encoding="utf-8")
lines = content.splitlines()

# Check for unclosed template literals
in_template = False
for i, line in enumerate(lines):
    backticks = line.count('`') - line.count('\\`')
    if backticks % 2 == 1:
        in_template = not in_template
        if in_template:
            print(f"L{i+1} UNCLOSED TEMPLATE: {line.rstrip()[:100]}")
if in_template:
    print("WARNING: File has unclosed template literal!")
else:
    print("All template literals balanced.")

# Check for <PageHeader that might not be self-closing
for i, line in enumerate(lines):
    if "PageHeader" in line and "<PageHeader" in line:
        # Check if it has /> at the end or on a subsequent line
        pass
    if "/>" in line and "PageHeader" in line:
        print(f"L{i+1} PageHeader self-closing: {line.strip()[:80]}")

# Now check with esbuild-style parsing
# Count ALL opening and closing JSX elements (not just div)
depth = 0
for i, line in enumerate(lines):
    s = re.sub(r'/\*.*?\*/', '', line)  # strip block comments
    s = re.sub(r'{/\*.*?\*/}', '', s)   # strip JSX comments
    
    # Count opening tags (element followed by space, >, or newline)
    opens = len(re.findall(r'<([A-Z][a-zA-Z]*|div|span|button|a|h[1-6]|p|ul|li|form|input|select|option|svg|g|text|line|rect|path|circle)\s', s))
    self_closes = len(re.findall(r'<([A-Z][a-zA-Z]*|div|span|button|a|h[1-6]|p|ul|li|form|input|select|option|svg|g|text|line|rect|path|circle)\s[^>]*/>', s))
    closes = len(re.findall(r'</([A-Z][a-zA-Z]*|div|span|button|a|h[1-6]|p|ul|li|form|input|select|option|svg|g|text|line|rect|path|circle)>', s))
    
    old = depth
    depth += opens - self_closes - closes
    
    if depth < 0:
        print(f"L{i+1:3d} NEGATIVE depth {old}->{depth}: {line.rstrip()[:80]}")

print(f"\nFinal JSX element depth: {depth}")

# Also count just div + PageHeader
div_opens = sum(len(re.findall(r'<div[\s>]', re.sub(r'{/\*.*?\*/}', '', l))) for l in lines)
div_closes = sum(len(re.findall(r'</div>', l)) for l in lines)
ph_self = sum(1 for l in lines if '<PageHeader' in l and '/>' in l)
print(f"div opens: {div_opens}, div closes: {div_closes}, balance: {div_opens - div_closes}")
print(f"PageHeader self-closing: {ph_self}")
