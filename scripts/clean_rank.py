import os

target_file = os.path.join(os.path.dirname(__file__), '..', 'component3', 'backend', 'routers', 'rank.py')
target_file = os.path.abspath(target_file)

with open(target_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where '<<<<<<< Updated upstream' starts and where '>>>>>>> Stashed changes' ends
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if '<<<<<<< Updated upstream' in line:
        start_idx = i
    if '>>>>>>> Stashed changes' in line:
        end_idx = i

if start_idx is not None and end_idx is not None:
    # Replace lines from start_idx to end_idx with '        return await _compute_single_job_pipeline(db, job_id)\n'
    new_lines = lines[:start_idx] + ['        return await _compute_single_job_pipeline(db, job_id)\n'] + lines[end_idx + 1:]
    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Removed conflict from line {start_idx} to {end_idx}")
else:
    print("Conflict markers not found")
