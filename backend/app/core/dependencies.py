from typing import Generator, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlmodel import Session, select

from backend.app.db.database import get_db
from backend.app.models.token import TokenPayload
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
) -> User:
    """
    Validate access token and return current user
    """
    try:
        payload = verify_token(token)
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.exec(select(User).where(User.id == int(token_data.sub))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify that the current user is active
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_current_active_superuser(
        current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Verify that the current user is a superuser
    """
    if "ADMIN" not in current_user.roles.split(","):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def check_roles(required_roles: List[str]):
    """
    Dependency factory to check if the current user has any of the required roles
    """
    async def _check_roles(
            current_user: User = Depends(get_current_active_user),
    ) -> User:
        user_roles = current_user.roles.split(",") if current_user.roles else []

        for role in required_roles:
            if role in user_roles:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return _check_roles