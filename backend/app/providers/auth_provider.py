from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import secrets
from fastapi import HTTPException, status
from sqlmodel import Session, select

from backend.app.models.user import User
from backend.app.models.token import RefreshToken
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.core.config import settings

class AuthProvider:
    """
    Authentication provider to handle user authentication and token management
    """

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password
        """
        user = db.exec(select(User).where(User.username == username)).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if user.disabled:
            return None

        return user

    @staticmethod
    def create_tokens(db: Session, user: User) -> Dict[str, Any]:
        """
        Create access and refresh tokens for a user
        """
        # Get user roles
        roles = user.roles.split(",") if user.roles else []

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id),
            username=user.username,
            roles=roles,
            expires_delta=access_token_expires
        )

        # Create refresh token
        refresh_token_value = secrets.token_hex(32)
        refresh_token = RefreshToken(
            token=refresh_token_value,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        db.add(refresh_token)
        db.commit()

        # Return tokens and user info
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "roles": roles,
        }

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh tokens using a refresh token
        """
        # Find the refresh token
        token = db.exec(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
                )
        ).first()

        if not token:
            return None

        # Get the user
        user = db.get(User, token.user_id)
        if not user or user.disabled:
            return None

        # Revoke the old token
        token.revoked = True
        db.add(token)
        db.commit()

        # Create new tokens
        return AuthProvider.create_tokens(db, user)

    @staticmethod
    def revoke_token(db: Session, refresh_token: str, user_id: int) -> bool:
        """
        Revoke a refresh token
        """
        token = db.exec(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.user_id == user_id,
                )
        ).first()

        if not token:
            return False

        token.revoked = True
        db.add(token)
        db.commit()

        return True

    @staticmethod
    def revoke_all_tokens(db: Session, user_id: int) -> bool:
        """
        Revoke all refresh tokens for a user
        """
        tokens = db.exec(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
                )
        ).all()

        for token in tokens:
            token.revoked = True
            db.add(token)

        db.commit()

        return True