"""Recruiter authentication: register, login, current user."""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app import security
from app.schemas import RecruiterLogin, RecruiterOut, RecruiterRegister, Token

router = APIRouter()


def public_recruiter(doc: dict) -> RecruiterOut:
    return RecruiterOut(
        id=str(doc["_id"]),
        full_name=doc["full_name"],
        email=doc["email"],
        organization=doc.get("organization"),
        created_at=doc["created_at"],
    )


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a recruiter account",
)
async def register(payload: RecruiterRegister, request: Request):
    db = request.app.state.db
    existing = await db.recruiters.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    now = datetime.now(timezone.utc)
    doc = {
        "full_name":    payload.full_name.strip(),
        "email":        payload.email,
        "password":     security.hash_password(payload.password),
        "organization": payload.organization,
        "created_at":   now,
    }
    result = await db.recruiters.insert_one(doc)
    token = security.create_access_token(str(result.inserted_id))
    return Token(access_token=token)


@router.post("/login", response_model=Token, summary="Log in a recruiter")
async def login(payload: RecruiterLogin, request: Request):
    db = request.app.state.db
    doc = await db.recruiters.find_one({"email": payload.email})
    if not doc or not security.verify_password(payload.password, doc["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = security.create_access_token(str(doc["_id"]))
    return Token(access_token=token)


async def get_current_recruiter(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    subject = security.decode_access_token(auth.split(" ", 1)[1].strip())
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    db = request.app.state.db
    doc = await db.recruiters.find_one({"_id": ObjectId(subject)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Recruiter no longer exists",
        )
    return doc


@router.get(
    "/me",
    response_model=RecruiterOut,
    summary="Get the authenticated recruiter",
)
async def me(recruiter: dict = Depends(get_current_recruiter)):
    return public_recruiter(recruiter)
