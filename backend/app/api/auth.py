from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
import secrets
from pydantic import BaseModel

from backend.app.models.token import Token, TokenResponse, RefreshRequest, RefreshToken, PasswordResetRequest, PasswordReset
from backend.app.models.user import User, UserResponse
from backend.app.core.config import settings
from backend.app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from backend.app.core.dependencies import get_current_active_user
from backend.app.db.database import get_db
from backend.app.providers.auth_provider import AuthProvider

router = APIRouter(prefix="/auth", tags=["authentication"])

# Simple login request model
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=TokenResponse)
async def login_json(
        login_data: LoginRequest,
        db: Session = Depends(get_db),
) -> Any:
    """
    Login with username and password (JSON)
    """
    user = AuthProvider.authenticate_user(db, login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = AuthProvider.create_tokens(db, user)
    return tokens

@router.post("/token", response_model=TokenResponse)
async def login_form(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
) -> Any:
    """
    OAuth2 compatible token login with form data
    """
    user = AuthProvider.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = AuthProvider.create_tokens(db, user)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        refresh_request: RefreshRequest,
        db: Session = Depends(get_db),
) -> Any:
    """
    Get a new access token using a refresh token
    """
    tokens = AuthProvider.refresh_tokens(db, refresh_request.refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tokens

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
        refresh_request: RefreshRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Logout the user by revoking the refresh token
    """
    success = AuthProvider.revoke_token(db, refresh_request.refresh_token, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        )

    return {"detail": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user information
    """
    return UserResponse.from_orm(current_user)

@router.post("/password-reset-request", status_code=status.HTTP_200_OK)
async def request_password_reset(
        reset_request: PasswordResetRequest,
        db: Session = Depends(get_db),
) -> Any:
    """
    Request a password reset token

    In a real application, this would send an email with a reset link.
    For this example, we'll just return the token in the response.
    """
    user = db.exec(select(User).where(User.email == reset_request.email)).first()

    # Always return success, even if user doesn't exist (security best practice)
    if not user:
        return {"detail": "If a user with this email exists, a password reset link has been sent."}

    # Create a reset token
    reset_token = secrets.token_urlsafe(32)

    # In a real app, you would store this token in the database and send it via email
    # For demo purposes, we'll just return it
    return {
        "detail": "Password reset requested. In a real app, an email would be sent.",
        "reset_token": reset_token  # Only for demo, don't do this in production!
    }

@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def reset_password(
        reset_data: PasswordReset,
        db: Session = Depends(get_db),
) -> Any:
    """
    Reset password using token

    In a real application, you would verify the token against stored tokens
    in the database. This is a simplified example.
    """
    # Example implementation would validate token and update password
    return {"detail": "Password has been reset successfully. You can now login with your new password."}