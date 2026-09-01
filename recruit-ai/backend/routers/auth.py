"""Authentication routes: company + candidate registration/login."""
import os
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.responses import FileResponse
from PIL import Image
from slowapi import Limiter
from slowapi.util import get_remote_address
from security import hash_password, verify_password, create_access_token, decode_access_token

from schemas import CompanyRegister, CandidateRegister, LoginRequest, Token, UserOut, ProfileUpdate, PasswordChange, ForgotPasswordRequest, ResetPasswordRequest

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def _user_out(doc: dict) -> UserOut:
    avatar_url = ""
    uid = str(doc["_id"])
    avatar_path = f"uploads/avatars/{uid}.jpg"
    if os.path.exists(avatar_path):
        avatar_url = f"/api/v1/auth/avatar/{uid}"
    return UserOut(
        id=uid,
        email=doc["email"],
        role=doc.get("role", "candidate"),
        name=doc.get("full_name", doc.get("company_name", "")),
        company_name=doc.get("company_name", ""),
        industry=doc.get("industry", ""),
        website=doc.get("website", ""),
        avatar_url=avatar_url,
        created_at=doc.get("created_at"),
    )


async def get_current_user(request: Request, required_role: str | None = None) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    data = decode_access_token(auth.split(" ", 1)[1].strip())
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    db = request.app.state.db
    doc = await db.users.find_one({"_id": ObjectId(data["sub"])})
    if not doc:
        raise HTTPException(status_code=401, detail="User not found")
    if required_role and doc.get("role") != required_role:
        raise HTTPException(status_code=403, detail=f"Requires role: {required_role}")
    return doc


async def require_company(request: Request) -> dict:
    return await get_current_user(request, "company")


async def require_candidate(request: Request) -> dict:
    return await get_current_user(request, "candidate")


# ── Company ─────────────────────────────────────────────────────
@router.post("/register/company", response_model=Token, status_code=201)
@limiter.limit("30/minute")
async def register_company(request: Request, payload: CompanyRegister):
    db = request.app.state.db
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    now = datetime.now(timezone.utc)
    doc = {
        "role": "company",
        "company_name": payload.company_name.strip(),
        "full_name": payload.company_name.strip(),
        "email": email,
        "password": hash_password(payload.password),
        "industry": payload.industry,
        "website": payload.website,
        "created_at": now,
    }
    result = await db.users.insert_one(doc)
    token = create_access_token(str(result.inserted_id), role="company")
    return Token(access_token=token, role="company", user_id=str(result.inserted_id))


@router.post("/login/company", response_model=Token)
@limiter.limit("30/minute")
async def login_company(request: Request, payload: LoginRequest):
    db = request.app.state.db
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="No account found with this email address")
    if user.get("role") != "company":
        raise HTTPException(status_code=400, detail="This account is registered as a Candidate. Please sign in via the Candidate Sign In page.")
    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password. Please verify and try again.")
    token = create_access_token(str(user["_id"]), role="company")
    return Token(access_token=token, role="company", user_id=str(user["_id"]))


# ── Candidate ───────────────────────────────────────────────────
@router.post("/register/candidate", response_model=Token, status_code=201)
@limiter.limit("30/minute")
async def register_candidate(request: Request, payload: CandidateRegister):
    db = request.app.state.db
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    now = datetime.now(timezone.utc)
    doc = {
        "role": "candidate",
        "full_name": payload.full_name.strip(),
        "email": email,
        "password": hash_password(payload.password),
        "created_at": now,
    }
    result = await db.users.insert_one(doc)
    token = create_access_token(str(result.inserted_id), role="candidate")
    return Token(access_token=token, role="candidate", user_id=str(result.inserted_id))


@router.post("/login/candidate", response_model=Token)
@limiter.limit("30/minute")
async def login_candidate(request: Request, payload: LoginRequest):
    db = request.app.state.db
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="No account found with this email address")
    if user.get("role") != "candidate":
        raise HTTPException(status_code=400, detail="This account is registered as an Employer. Please sign in via the Employer Sign In page.")
    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password. Please verify and try again.")
    token = create_access_token(str(user["_id"]), role="candidate")
    return Token(access_token=token, role="candidate", user_id=str(user["_id"]))



# ── Forgot / Reset ──────────────────────────────────────────────
import secrets

@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(request: Request, payload: ForgotPasswordRequest):
    db = request.app.state.db
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    # Always return success to avoid email enumeration
    if not user:
        return {"success": True, "message": "If an account exists, a reset link has been generated.", "reset_token": None}
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc).timestamp() + 900  # 15 min
    await db.password_resets.update_many({"email": email, "used": False}, {"$set": {"used": True}})
    await db.password_resets.insert_one({"email": email, "user_id": str(user["_id"]), "role": user.get("role","candidate"), "token": token, "expires_at": expires, "used": False, "created_at": datetime.now(timezone.utc)})
    # For demo, return token directly (in prod, email it)
    return {"success": True, "message": "If an account exists, a reset link has been generated.", "reset_token": token, "expires_in": 900}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, payload: ResetPasswordRequest):
    db = request.app.state.db
    doc = await db.password_resets.find_one({"token": payload.token, "used": False})
    if not doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if datetime.now(timezone.utc).timestamp() > doc["expires_at"]:
        await db.password_resets.update_one({"_id": doc["_id"]}, {"$set": {"used": True}})
        raise HTTPException(status_code=400, detail="Reset token has expired")
    user = await db.users.find_one({"_id": ObjectId(doc["user_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"password": hash_password(payload.new_password)}})
    await db.password_resets.update_one({"_id": doc["_id"]}, {"$set": {"used": True}})
    return {"success": True, "message": "Password has been reset. Please sign in."}


# ── Common ──────────────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
async def me(user: dict = Depends(get_current_user)):
    return _user_out(user)


@router.get("/profile", response_model=UserOut)
async def get_profile(user: dict = Depends(get_current_user)):
    return _user_out(user)


@router.put("/profile", response_model=UserOut)
async def update_profile(payload: ProfileUpdate, request: Request, user: dict = Depends(get_current_user)):
    db = request.app.state.db
    update_fields = {}
    if payload.full_name is not None:
        update_fields["full_name"] = payload.full_name.strip()
    if payload.company_name is not None:
        update_fields["company_name"] = payload.company_name.strip()
    if payload.industry is not None:
        update_fields["industry"] = payload.industry.strip()
    if payload.website is not None:
        update_fields["website"] = payload.website.strip()
    if update_fields:
        await db.users.update_one({"_id": user["_id"]}, {"$set": update_fields})
    updated = await db.users.find_one({"_id": user["_id"]})
    return _user_out(updated)


@router.put("/password")
async def change_password(payload: PasswordChange, request: Request, user: dict = Depends(get_current_user)):
    if not verify_password(payload.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    db = request.app.state.db
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"password": hash_password(payload.new_password)}})
    return {"success": True, "message": "Password changed"}


@router.post("/avatar")
async def upload_avatar(request: Request, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP images allowed")
    data = await file.read()
    if len(data) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 2MB")
    os.makedirs("uploads/avatars", exist_ok=True)
    path = f"uploads/avatars/{str(user['_id'])}.jpg"
    img = Image.open(__import__("io").BytesIO(data))
    img.thumbnail((200, 200))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(path, "JPEG", quality=85)
    avatar_url = f"/api/v1/auth/avatar/{str(user['_id'])}"
    db = request.app.state.db
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"avatar_url": avatar_url}})
    return {"success": True, "avatar_url": avatar_url}


@router.get("/avatar/{user_id}")
async def get_avatar(user_id: str):
    import re
    if not re.match(r'^[A-Za-z0-9_\-]+$', user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    path = f"uploads/avatars/{user_id}.jpg"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Avatar not found")
    return FileResponse(path, media_type="image/jpeg")
