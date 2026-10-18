"""Fix SkillGap.jsx: remove premature close (lines 417-419), apply all pending fixes."""
import pathlib

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

# ── Fix 1: Add useSearchParams import (line 2) ──
for i, line in enumerate(lines):
    if "useNavigate, Link" in line:
        lines[i] = line.replace("useNavigate, Link", "useNavigate, Link, useSearchParams")
        break

# ── Fix 2: Add userRole + paramJobId declarations after useAuth (line ~18) ──
for i, line in enumerate(lines):
    if "const candidateId = localStorage.getItem" in line:
        indent = "  "
        lines.insert(i + 1, f"{indent}const [searchParams] = useSearchParams()\n")
        lines.insert(i + 2, f"{indent}const paramJobId = searchParams.get('jobId')\n")
        lines.insert(i + 3, f"{indent}const userRole = localStorage.getItem('recruitai.role') || 'candidate'\n")
        break

# ── Fix 3: Replace arr→reports in loadAppliedJobsAnalysis (only inside that function) ──
in_load_applied = False
new_lines = []
for i, line in enumerate(lines):
    if "const loadAppliedJobsAnalysis" in line:
        in_load_applied = True
    elif in_load_applied and (line.strip().startswith("const ") and "=" in line and "loadApplied" not in line):
        in_load_applied = False

    if in_load_applied:
        line = line.replace("if (arr.length === 0)", "if (reports.length === 0)")
        line = line.replace("arr.some", "reports.some")
        line = line.replace("arr[0]", "reports[0]")
    new_lines.append(line)
lines = new_lines

# ── Fix 4: Remove ONLY the premature close (lines 417-419 in ORIGINAL) ──
# After fix inserts, line numbers shifted by +3. Original 417-419 → now 420-422.
# Find the pattern: after Tab 1 conditional close, find 3 lines that close
# outer div / return / function prematurely.
# Pattern: "    </div>\n  )\n}\n" immediately before the TAB 2 comment.

tab2_idx = None
for i, line in enumerate(lines):
    if "{/* TAB 2: EXPLORER & WHAT-IF SIMULATOR */}" in line:
        tab2_idx = i
        break

if tab2_idx is not None:
    # The 3 lines before TAB 2 comment should be: </div>,  ),  }
    check_start = tab2_idx - 3
    if check_start >= 0:
        l0 = lines[check_start].strip()
        l1 = lines[check_start + 1].strip()
        l2 = lines[check_start + 2].strip()
        if l0 == "</div>" and l1 == ")" and l2 == "}":
            del lines[check_start:tab2_idx]
            print(f"Removed premature close at original lines {check_start+1}-{tab2_idx}")
        else:
            # Try 5 lines back (in case the count is different)
            check_start = tab2_idx - 5
            if check_start >= 0:
                l0 = lines[check_start].strip()
                l1 = lines[check_start + 1].strip()
                l2 = lines[check_start + 2].strip()
                l3 = lines[check_start + 3].strip()
                l4 = lines[check_start + 4].strip()
                if l2 == "</div>" and l3 == ")" and l4 == "}":
                    del lines[check_start + 2:tab2_idx]
                    print(f"Removed premature close at original lines {check_start+3}-{tab2_idx}")
                else:
                    print(f"WARNING: Could not find premature close pattern. Lines around TAB 2:")
                    for j in range(max(0, tab2_idx-6), tab2_idx+1):
                        print(f"  {j+1}: {lines[j].rstrip()}")
    else:
        print(f"WARNING: Not enough lines before TAB 2 comment at line {tab2_idx+1}")

path.write_text("".join(lines), encoding="utf-8")
print(f"Done! File has {len(lines)} lines.")
