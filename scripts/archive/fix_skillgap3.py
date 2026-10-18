"""Simple targeted fix for SkillGap.jsx."""
import pathlib

path = pathlib.Path(r"C:\Users\ASUS\OneDrive\Documents\GitHub\R26-IT-148\frontend\src\pages\SkillGap.jsx")
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
print(f"Original: {len(lines)} lines")

# 1. Add useSearchParams to import on line 2 (index 1)
lines[1] = lines[1].replace("useNavigate, Link", "useNavigate, Link, useSearchParams")

# 2. Insert userRole/paramJobId after line 18 (index 17, the candidateId line)
# Insert at index 18 (after candidateId line)
insert_lines = [
    "  const [searchParams] = useSearchParams()\n",
    "  const paramJobId = searchParams.get('jobId')\n",
    "  const userRole = localStorage.getItem('recruitai.role') || 'candidate'\n",
]
for j, insert_line in enumerate(insert_lines):
    lines.insert(18 + j, insert_line)

print(f"After inserts: {len(lines)} lines")

# 3. Delete the premature close: lines 420-422 (1-indexed) = indices 419-421
# After inserting 3 lines, original line 417 = index 419, line 418 = 420, line 419 = 421
# Verify these are the right lines
print(f"Line 420: {lines[419].rstrip()}")
print(f"Line 421: {lines[420].rstrip()}")
print(f"Line 422: {lines[421].rstrip()}")

# These should be: "    </div>", "  )", "}"
assert lines[419].strip() == "</div>", f"Expected </div>, got: {lines[419].strip()}"
assert lines[420].strip() == ")", f"Expected ), got: {lines[420].strip()}"
assert lines[421].strip() == "}", f"Expected }}, got: {lines[421].strip()}"

del lines[419:422]
print(f"After deleting premature close: {len(lines)} lines")

# 4. Fix arr -> reports in loadAppliedJobsAnalysis (lines 83-88 after insert = indices 82-87)
for i in range(len(lines)):
    if "if (arr.length === 0)" in lines[i]:
        lines[i] = lines[i].replace("if (arr.length === 0)", "if (reports.length === 0)")
    elif "arr.some((a) => a.job_id === paramJobId)" in lines[i]:
        lines[i] = lines[i].replace("arr.some((a) => a.job_id === paramJobId)", "reports.some((a) => a.job_id === paramJobId)")
    elif "arr.some((a) => a.job_id === selectedJobId)" in lines[i]:
        lines[i] = lines[i].replace("arr.some((a) => a.job_id === selectedJobId)", "reports.some((a) => a.job_id === selectedJobId)")
    elif "setSelectedJobId(arr[0].job_id)" in lines[i]:
        lines[i] = lines[i].replace("setSelectedJobId(arr[0].job_id)", "setSelectedJobId(reports[0].job_id)")

path.write_text("".join(lines), encoding="utf-8")
print(f"Final: {len(lines)} lines")
print("Done!")
