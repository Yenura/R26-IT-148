"""Ranked shortlist for a job posting using component3's CSS engine.

Candidate features come from this service's ``applications`` collection; the
candidate's latest skill-gap report is read (read-only) from component4's
Mongo database.
"""

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request

from app import config
from app.engine_link import (
    CSSEngine,
    JobRequirementProfile,
    build_features,
    normalise_role,
)
from app.routers.auth import get_current_recruiter
from app.schemas import RankedCandidate, RankedListResponse

router = APIRouter()


async def _fetch_job(db, job_id: str, recruiter_id: str) -> dict:
    try:
        oid = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    doc = await db.job_postings.find_one({"_id": oid, "recruiter_id": ObjectId(recruiter_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return doc


def _p_score(app_value: float | None, report_value: float | None, /) -> float:
    if app_value is not None:
        return app_value / 100.0
    if report_value is not None:
        return report_value / 100.0
    return 0.0


@router.get(
    "/{job_id}/candidates",
    response_model=RankedListResponse,
    summary="Rank applicants for a job using the CSS scoring engine",
)
async def rank_candidates(
    job_id: str,
    request: Request,
    recruiter: dict = Depends(get_current_recruiter),
):
    db = request.app.state.db
    reports_db = request.app.state.reports_db
    job = await _fetch_job(db, job_id, str(recruiter["_id"]))

    role_key = normalise_role(job["role_key"])
    job_profile = JobRequirementProfile.from_role(role_key)
    engine = CSSEngine(job_profile)

    # Latest application per candidate (dedupe repeated applications).
    apps = await db.applications.find({"job_id": job["_id"]}).sort("applied_at", -1).to_list(1000)
    seen: set[str] = set()
    features = []
    for app in apps:
        if app["candidate_id"] in seen:
            continue
        seen.add(app["candidate_id"])

        report = None
        try:
            report = await getattr(reports_db, config.REPORTS_COLLECTION).find_one(
                {"candidate_id": app["candidate_id"]},
                sort=[("analysis_timestamp", -1)],
            )
        except Exception:
            report = None

        report_interview = (report or {}).get("interview_score")
        skill_raw = None
        if report is not None and report.get("skill_match_pct") is not None:
            skill_raw = report["skill_match_pct"] / 100.0
        elif app.get("cv_matching_score") is not None:
            skill_raw = app["cv_matching_score"] / 100.0
        else:
            skill_raw = 0.0

        features.append(
            build_features(
                candidate_id=app["candidate_id"],
                role_key=role_key,
                experience_years=float(app.get("experience_years") or 0),
                education=app.get("education"),
                skill_score_raw=skill_raw,
                p_mcq=_p_score(app.get("mcq_score"), report_interview),
                p_desc=_p_score(app.get("descriptive_score"), report_interview),
                p_code=_p_score(app.get("coding_score"), report_interview),
            )
        )

    scored = engine.rank_pool(features)
    report_by_candidate = {}
    if features:
        candidate_ids = [f.candidate_id for f in features]
        cursor = getattr(reports_db, config.REPORTS_COLLECTION).find(
            {"candidate_id": {"$in": candidate_ids}}
        ).sort("analysis_timestamp", -1)
        async for doc in cursor:
            if doc["candidate_id"] not in report_by_candidate:
                report_by_candidate[doc["candidate_id"]] = doc

    names = {a["candidate_id"]: a["candidate_name"] for a in apps}

    candidates = []
    for s in scored:
        report = report_by_candidate.get(s.candidate_id)
        candidates.append(
            RankedCandidate(
                rank=s.rank,
                candidate_id=s.candidate_id,
                candidate_name=names.get(s.candidate_id, s.candidate_id),
                job_role=role_key,
                CSS=s.CSS,
                S_cv=s.S_cv,
                S_int=s.S_int,
                S_edu=s.S_edu,
                S_exp=s.S_exp,
                S_skill=s.S_skill,
                P_mcq=s.P_mcq,
                P_desc=s.P_desc,
                P_code=s.P_code,
                passed_hard_filter=s.passed_hard_filter,
                filter_fail_reason=s.filter_fail_reason,
                hire_probability=(report or {}).get("hire_probability"),
                report_available=report is not None,
            )
        )

    return RankedListResponse(
        job_id=job_id,
        job_title=job["title"],
        job_role=job["job_role"],
        total=len(candidates),
        candidates=candidates,
    )
