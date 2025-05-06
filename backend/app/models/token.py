from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from pydantic import BaseModel

class Token(BaseModel):
    """
    Response model for token
    """
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """
    Model for JWT payload
    """
    sub: str  # user id
    username: str
    roles: List[str]
    exp: datetime
    iat: datetime

class TokenResponse(Token):
    """
    Extended token response with user info
    """
    user_id: int
    username: str
    roles: List[str]

class RefreshToken(SQLModel, table=True):
    """
    Database model for refresh tokens
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(index=True, unique=True)
    user_id: int = Field(index=True)  # No foreign key for simplicity
    expires_at: datetime
    revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RefreshRequest(BaseModel):
    """
    Model for refresh token request
    """
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """
    Model for password reset request
    """
    email: str

class PasswordReset(BaseModel):
    """
    Model for password reset
    """
    token: str
    new_password: str
