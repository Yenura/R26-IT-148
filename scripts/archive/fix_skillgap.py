"""Fix SkillGap.jsx: move orphaned Tabs 2&3 inside the return, apply all pending fixes."""
import pathlib, re

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

# ── Fix 1: Add useSearchParams import (line 2) ──
for i, line in enumerate(lines):
    if "useNavigate, Link" in line:
        lines[i] = line.replace(
            "useNavigate, Link",
            "useNavigate, Link, useSearchParams"
        )
        break

# ── Fix 2: Add userRole + paramJobId declarations after useAuth (line ~18) ──
for i, line in enumerate(lines):
    if "const candidateId = localStorage.getItem" in line:
        indent = "  "
        lines.insert(i + 1, f"{indent}const [searchParams] = useSearchParams()\n")
        lines.insert(i + 2, f"{indent}const paramJobId = searchParams.get('jobId')\n")
        lines.insert(i + 3, f"{indent}const userRole = localStorage.getItem('recruitai.role') || 'candidate'\n")
        break

# ── Fix 3: Replace arr→reports in loadAppliedJobsAnalysis (lines ~80-86) ──
# The variable is named `reports` (line 74) but the code references `arr`
new_lines = []
for i, line in enumerate(lines):
    # Only replace arr references inside loadAppliedJobsAnalysis (between "const loadAppliedJobsAnalysis" and the next "const ")
    if "if (arr.length === 0)" in line or "arr.some" in line:
        line = line.replace("arr.length", "reports.length").replace("arr.some", "reports.some").replace("arr[0]", "reports[0]")
    new_lines.append(line)
lines = new_lines

# ── Fix 4: Remove premature function close (lines 415-419 in original) ──
# These are the 5 lines: </div>  )}  </div>  )  }
# After the Tab 1 conditional close, these prematurely close outer div + return + function
# We identify them by finding the pattern: after the Tab 1 block ends, there are
# closing tags that shouldn't be there yet.

# Strategy: find the "loadAppliedJobsAnalysis" async function's closing brace
# and find the "return (" line. The premature close is after Tab 1's conditional.

# Find the exact lines to remove: they are 5 consecutive lines after line 415 in the
# Tab 1 content that close prematurely.
# Line numbers (0-indexed): 414=</div> 415=)} 416=</div> 417=)  418=}
# We want to remove all 5 lines.

# Find by looking for the pattern after the "selectedReport" conditional block ends
# and before the Tab 2 comment.
premature_close_start = None
for i, line in enumerate(lines):
    if "{/* TAB 2: EXPLORER & WHAT-IF SIMULATOR */}" in line:
        # The 5 lines before this are the premature close
        # But we need to verify: they should be </div>,  )},  </div>,  ),  }
        candidate_start = i - 5
        if candidate_start >= 0:
            test = "".join(lines[candidate_start:i])
            # Check for the pattern
            if "</div>" in lines[candidate_start] and ")}" in lines[candidate_start + 1]:
                premature_close_start = candidate_start
                premature_close_end = i  # exclusive
                break

if premature_close_start is not None:
    # Remove the 5 premature closing lines
    del lines[premature_close_start:premature_close_end]
    print(f"Removed premature close at lines {premature_close_start+1}-{premature_close_end}")
else:
    print("WARNING: Could not find premature close pattern")

# ── Fix 5: Fix the orphaned Tab 3 end-of-file closings ──
# The original file ends with:
#   </div>   (orphaned, was closing outer div)
#   )        (orphaned, was closing return)
#   }        (orphaned, was closing function)
# These are inside Tab 3's content at the wrong depth.
# We need to replace them with properly nested closings.

# Find the last 3 lines and verify they are the orphaned closings
last_lines = lines[-3:]
if last_lines[0].strip() == "</div>" and last_lines[1].strip() == ")" and last_lines[2].strip() == "}":
    # These are the orphaned closings. Remove them.
    lines = lines[:-3]
    print("Removed orphaned end-of-file closings")

# ── Fix 6: Add proper closing at end of file ──
# Now the file ends after Tab 3's closing (which is inside the Tab 3 conditional).
# We need to close: outer div, return ), function }
# The structure should be:
#   {activeTab === 'graph' && (...)}
#   </div>    ← outer div (from return)
#   )         ← return close
# }           ← function close

lines.append("    </div>\n")
lines.append("  )\n")
lines.append("}\n")
print("Added proper closing: </div>, ), }")

# ── Write back ──
path.write_text("".join(lines), encoding="utf-8")
print(f"\nDone! File has {len(lines)} lines.")
