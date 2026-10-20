import os

# 1. Patch analytics.py
analytics_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'component4', 'backend', 'routers', 'analytics.py'))
with open(analytics_file, 'r', encoding='utf-8') as f:
    analytics_content = f.read()

# Replace the sequential async for loops with parallel queries in leaderboard()
old_analytics_block = '''    # Batch fetch in 4 queries
    resumes_map = {}
    async for r in db.resumes.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(r.get("candidate_id", ""))
        if cid not in resumes_map:
            resumes_map[cid] = r

    preds_map = {}
    async for p in db.predictions.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(p.get("candidate_id", ""))
        if cid not in preds_map:
            preds_map[cid] = p

    results_map = {}
    async for res in db.results.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(res.get("candidate_id", ""))
        if cid not in results_map:
            results_map[cid] = res

    scores_map = {}
    async for sc in db.interview_scores.find({"$or": [{"candidate_id": {"$in": candidate_ids}}, {"candidate_id": {"$in": obj_ids}}]}).sort("created_at", -1):
        cid = str(sc.get("candidate_id", ""))
        if cid not in scores_map:
            scores_map[cid] = sc'''

new_analytics_block = '''    # Optimized concurrent parallel batch fetch with projection
    c_in = list(set(candidate_ids + [str(o) for o in obj_ids])) + obj_ids
    r_task = db.resumes.find({"candidate_id": {"$in": c_in}}, projection={"candidate_id": 1, "skills": 1, "experience_years": 1, "education": 1, "created_at": 1}).sort("created_at", -1).to_list(300)
    p_task = db.predictions.find({"candidate_id": {"$in": c_in}}, projection={"candidate_id": 1, "predicted_role": 1, "overall_score": 1, "skill_score": 1, "created_at": 1}).sort("created_at", -1).to_list(300)
    res_task = db.results.find({"candidate_id": {"$in": c_in}}).sort("created_at", -1).to_list(300)
    s_task = db.interview_scores.find({"candidate_id": {"$in": c_in}}).sort("created_at", -1).to_list(300)

    r_list, p_list, res_list, s_list = await asyncio.gather(r_task, p_task, res_task, s_task)

    resumes_map = {}
    for r in r_list:
        cid = str(r.get("candidate_id", ""))
        if cid and cid not in resumes_map:
            resumes_map[cid] = r

    preds_map = {}
    for p in p_list:
        cid = str(p.get("candidate_id", ""))
        if cid and cid not in preds_map:
            preds_map[cid] = p

    results_map = {}
    for res in res_list:
        cid = str(res.get("candidate_id", ""))
        if cid and cid not in results_map:
            results_map[cid] = res

    scores_map = {}
    for sc in s_list:
        cid = str(sc.get("candidate_id", ""))
        if cid and cid not in scores_map:
            scores_map[cid] = sc'''

if old_analytics_block in analytics_content:
    analytics_content = analytics_content.replace(old_analytics_block, new_analytics_block)
    analytics_content = analytics_content.replace('_LEADERBOARD_CACHE["expires_at"] = now_ts + 45.0', '_LEADERBOARD_CACHE["expires_at"] = now_ts + 180.0')
    with open(analytics_file, 'w', encoding='utf-8') as f:
        f.write(analytics_content)
    print("Successfully patched analytics.py")
else:
    print("analytics.py target block not found, check lines")

# 2. Patch skill_gap.py
skill_gap_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'component4', 'backend', 'routers', 'skill_gap.py'))
with open(skill_gap_file, 'r', encoding='utf-8') as f:
    sg_content = f.read()

sg_content = sg_content.replace('_CACHE_TTL_SECS = 45.0', '_CACHE_TTL_SECS = 180.0')
old_sg_filters = '''    cand_id_filters = [{"candidate_id": candidate_id}]
    if ObjectId.is_valid(candidate_id):
        cand_id_filters.append({"candidate_id": ObjectId(candidate_id)})
        cand_id_filters.append({"_id": ObjectId(candidate_id)})

    # Parallel batch fetch of candidate's core collections
    resumes_task = db.resumes.find({"$or": [{"candidate_id": candidate_id}] + ([{"candidate_id": ObjectId(candidate_id)}] if ObjectId.is_valid(candidate_id) else [])}).sort("created_at", -1).to_list(10)
    apps_task = db.applications.find({"$or": cand_id_filters}).sort("applied_at", -1).to_list(100)
    preds_task = db.predictions.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)
    scores_task = db.interview_scores.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)
    results_task = db.results.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)
    sessions_task = db.sessions.find({"$or": cand_id_filters}).sort("created_at", -1).to_list(100)
    cv_analyses_task = db.cv_analyses.find({"$or": cand_id_filters}).sort("analysis_timestamp", -1).to_list(100)'''

new_sg_filters = '''    cand_id_keys = [candidate_id]
    if ObjectId.is_valid(candidate_id):
        cand_id_keys.append(ObjectId(candidate_id))

    # Parallel batch fetch of candidate's core collections using indexed $in
    resumes_task = db.resumes.find({"candidate_id": {"$in": cand_id_keys}}).sort("created_at", -1).to_list(10)
    apps_task = db.applications.find({"candidate_id": {"$in": cand_id_keys}}).sort("applied_at", -1).to_list(100)
    preds_task = db.predictions.find({"candidate_id": {"$in": cand_id_keys}}).sort("created_at", -1).to_list(100)
    scores_task = db.interview_scores.find({"candidate_id": {"$in": cand_id_keys}}).sort("created_at", -1).to_list(100)
    results_task = db.results.find({"candidate_id": {"$in": cand_id_keys}}).sort("created_at", -1).to_list(100)
    sessions_task = db.sessions.find({"candidate_id": {"$in": cand_id_keys}}).sort("created_at", -1).to_list(100)
    cv_analyses_task = db.cv_analyses.find({"candidate_id": {"$in": cand_id_keys}}).sort("analysis_timestamp", -1).to_list(100)'''

if old_sg_filters in sg_content:
    sg_content = sg_content.replace(old_sg_filters, new_sg_filters)
    with open(skill_gap_file, 'w', encoding='utf-8') as f:
        f.write(sg_content)
    print("Successfully patched skill_gap.py")
else:
    print("skill_gap.py target block not found, check lines")
