"""Unified backend configuration."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("FATAL: MONGODB_URI not set. Copy .env.example to .env and fill in credentials.", file=sys.stderr)
    sys.exit(1)

DB_NAME = os.getenv("DB_NAME", "HR")
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    print("FATAL: JWT_SECRET not set. Copy .env.example to .env and set a secure secret.", file=sys.stderr)
    sys.exit(1)

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5174").split(",")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Outbound email (optional). When SMTP_HOST is unset, no mail is sent and
# flows that need email (e.g. password reset) degrade gracefully.
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "RecruitAI <no-reply@recruitai.local>")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "1") == "1"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5174")
