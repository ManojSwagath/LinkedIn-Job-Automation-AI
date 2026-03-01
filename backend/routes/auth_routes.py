"""
Authentication API routes for AutoAgentHire.

Endpoints
---------
POST /auth/signup   – Register a new user
POST /auth/login    – Authenticate and receive a JWT
GET  /auth/me       – Return the current authenticated user's profile
POST /auth/google   – Sign in / register with a Google ID token
"""

import os
import uuid as _uuid
import requests as http_requests
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend.auth.password import hash_password, verify_password
from backend.auth.jwt import create_access_token
from backend.auth.validators import validate_email_format, validate_password_strength
from backend.auth.dependencies import get_current_user
from backend.database.connection import get_db
from backend.database.crud import UserRepository
from backend.database.models import User

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Request / Response schemas ────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    full_name: str | None = None


class SignupResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: int
    uuid: str
    email: str
    full_name: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime | None = None
    last_login: datetime | None = None

    class Config:
        from_attributes = True


class GoogleAuthRequest(BaseModel):
    access_token: str = Field(..., description="Google OAuth2 access token from useGoogleLogin")


# ── Signup ────────────────────────────────────────────────────────────────────

@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account.

    1. Validate email format (backend re-check).
    2. Validate password strength.
    3. Ensure email is not already registered.
    4. Hash password with bcrypt and persist the user.
    """

    # 1. Email format (pydantic already validates via EmailStr, but we add our own)
    email_err = validate_email_format(body.email)
    if email_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=email_err)

    # 2. Password strength
    pw_err = validate_password_strength(body.password)
    if pw_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pw_err)

    # 3. Duplicate check
    existing = UserRepository.get_by_email(db, email=body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists. Please login.",
        )

    # 4. Hash + store
    hashed = hash_password(body.password)
    UserRepository.create(
        db,
        email=body.email,
        hashed_password=hashed,
        full_name=body.full_name or "",
    )

    return SignupResponse(message="User created successfully")


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and get JWT token",
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token.

    Algorithm
    ---------
    1. Validate email format.
    2. Look up user by email.
    3. If not found → 401 "Invalid credentials. Please sign up first."
    4. Compare password with stored hash via bcrypt.
    5. If mismatch → 401 "Incorrect password."
    6. On success → issue JWT with ``sub=email``.
    """

    # 1. Email format
    email_err = validate_email_format(body.email)
    if email_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=email_err)

    # 2. Look up user
    user = UserRepository.get_by_email(db, email=body.email)

    # 3. Not found
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please sign up first.",
        )

    # 4-5. Verify password
    # In SQLAlchemy models, instance attributes are proxy descriptors at class level
    # but resolve to python types at instance level. We suppress the static analysis error.
    if not verify_password(body.password, str(user.hashed_password)):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )

    # Update last_login timestamp
    try:
        UserRepository.update(db, int(user.id), last_login=datetime.now(timezone.utc))  # type: ignore
    except Exception:
        pass  # non-critical – don't fail the login

    # 6. Issue token
    access_token = create_access_token(data={"sub": user.email})

    return LoginResponse(access_token=access_token)


# ── Current user profile ─────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.post(
    "/google",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in or register with Google",
)
def google_auth(body: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Verify a Google OAuth2 access token, then sign in or auto-register the user.

    Flow
    ----
    1. Call Google's userinfo endpoint with the access token to verify it.
    2. Extract email + name from the verified payload.
    3. Find or create the user in the database.
    4. Return our own JWT access token.
    """
    # 1. Verify token by calling Google's userinfo endpoint
    try:
        resp = http_requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {body.access_token}"},
            timeout=10,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach Google servers: {exc}",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google access token.",
        )

    userinfo = resp.json()
    google_email: str = userinfo.get("email", "")
    google_name: str = userinfo.get("name", "")
    email_verified: bool = userinfo.get("email_verified", False)

    if not google_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account has no email address.",
        )
    if not email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google email is not verified.",
        )

    # 2. Find or create user
    user = UserRepository.get_by_email(db, email=google_email)
    if user is None:
        # Auto-register: generate a random secure password (the user won't use it)
        random_pw = hash_password(_uuid.uuid4().hex + _uuid.uuid4().hex)
        user = UserRepository.create(
            db,
            email=google_email,
            hashed_password=random_pw,
            full_name=google_name,
        )

    # 3. Update last_login
    try:
        UserRepository.update(db, int(user.id), last_login=datetime.now(timezone.utc))  # type: ignore
    except Exception:
        pass

    # 4. Issue our JWT
    access_token = create_access_token(data={"sub": user.email})
    return LoginResponse(access_token=access_token)
