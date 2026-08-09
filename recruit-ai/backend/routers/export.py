"""Export routes: CSV, PDF, Excel."""
import io
import csv
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from routers.auth import get_current_user

router = APIRouter()


@router.get("/csv")
async def export_csv(
    request: Request,
    type: str = "predictions",
    user: dict = Depends(get_current_user),
):
    db = request.app.state.db
    output = io.StringIO()
    writer = csv.writer(output)

    if type == "predictions":
        cursor = db.predictions.find({"candidate_id": str(user["_id"])})
        docs = await cursor.to_list(length=500)
        writer.writerow(["ID", "Predicted Role", "Confidence", "Semantic Score",
                         "Skill Score", "Experience Score", "Education Score",
                         "Overall Score", "Matched Skills", "Missing Skills", "Created At"])
        for d in docs:
            writer.writerow([
                str(d.get("_id", "")),
                d.get("predicted_role", ""),
                d.get("role_confidence", 0),
                d.get("semantic_score", 0),
                d.get("skill_score", 0),
                d.get("experience_score", 0),
                d.get("education_score", 0),
                d.get("overall_score", 0),
                "; ".join(d.get("matched_skills", [])),
                "; ".join(d.get("missing_skills", [])),
                d.get("created_at", ""),
            ])
    elif type == "resumes":
        cursor = db.resumes.find({"candidate_id": str(user["_id"])})
        docs = await cursor.to_list(length=500)
        writer.writerow(["ID", "Filename", "Name", "Email", "Phone", "Skills",
                         "Education", "Experience Years", "Created At"])
        for d in docs:
            writer.writerow([
                str(d.get("_id", "")),
                d.get("filename", ""),
                d.get("candidate_name", ""),
                d.get("email", ""),
                d.get("phone", ""),
                "; ".join(d.get("skills", [])),
                d.get("education", ""),
                d.get("experience_years", 0),
                d.get("created_at", ""),
            ])
    else:
        raise HTTPException(status_code=400, detail="type must be 'predictions' or 'resumes'")

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={type}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"},
    )


@router.get("/excel")
async def export_excel(
    request: Request,
    type: str = "predictions",
    user: dict = Depends(get_current_user),
):
    try:
        import openpyxl
    except ImportError:
        raise HTTPException(status_code=500, detail="openpyxl not installed")

    db = request.app.state.db
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = type.capitalize()

    if type == "predictions":
        cursor = db.predictions.find({"candidate_id": str(user["_id"])})
        docs = await cursor.to_list(length=500)
        ws.append(["ID", "Predicted Role", "Confidence", "Semantic Score",
                    "Skill Score", "Exp Score", "Edu Score", "Overall Score", "Created At"])
        for d in docs:
            ws.append([
                str(d.get("_id", "")), d.get("predicted_role", ""),
                d.get("role_confidence", 0), d.get("semantic_score", 0),
                d.get("skill_score", 0), d.get("experience_score", 0),
                d.get("education_score", 0), d.get("overall_score", 0),
                str(d.get("created_at", "")),
            ])
    elif type == "resumes":
        cursor = db.resumes.find({"candidate_id": str(user["_id"])})
        docs = await cursor.to_list(length=500)
        ws.append(["ID", "Filename", "Name", "Email", "Skills", "Education", "Exp Years"])
        for d in docs:
            ws.append([
                str(d.get("_id", "")), d.get("filename", ""),
                d.get("candidate_name", ""), d.get("email", ""),
                "; ".join(d.get("skills", [])), d.get("education", ""),
                d.get("experience_years", 0),
            ])
    else:
        raise HTTPException(status_code=400, detail="type must be 'predictions' or 'resumes'")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={type}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.xlsx"},
    )


@router.get("/pdf")
async def export_pdf(
    request: Request,
    type: str = "predictions",
    user: dict = Depends(get_current_user),
):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab not installed")

    db = request.app.state.db
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"RecruitAI - {type.capitalize()} Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    if type == "predictions":
        cursor = db.predictions.find({"candidate_id": str(user["_id"])})
        docs = await cursor.to_list(length=500)
        data = [["Role", "Confidence", "Semantic", "Skill", "Exp", "Edu", "Overall"]]
        for d in docs:
            data.append([
                d.get("predicted_role", ""),
                f"{d.get('role_confidence', 0):.1%}",
                f"{d.get('semantic_score', 0):.1f}",
                f"{d.get('skill_score', 0):.1f}",
                f"{d.get('experience_score', 0):.1f}",
                f"{d.get('education_score', 0):.1f}",
                f"{d.get('overall_score', 0):.1f}",
            ])
    elif type == "resumes":
        cursor = db.resumes.find({"candidate_id": str(user["_id"])})
        docs = await cursor.to_list(length=500)
        data = [["Name", "Email", "Skills", "Education", "Exp"]]
        for d in docs:
            data.append([
                d.get("candidate_name", ""),
                d.get("email", ""),
                ", ".join(d.get("skills", [])[:5]),
                d.get("education", ""),
                str(d.get("experience_years", 0)),
            ])
    else:
        raise HTTPException(status_code=400, detail="type must be 'predictions' or 'resumes'")

    if len(data) > 1:
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a36")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No data available.", styles["Normal"]))

    doc.build(elements)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={type}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"},
    )
