from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from pydantic import EmailStr

class UserBase(SQLModel):
    """
    Base model for user information
    """
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    full_name: Optional[str] = None
    disabled: bool = Field(default=False)
    tenant: str = Field(default="default", index=True)  # For multi-tenant support

class User(UserBase, table=True):
    """
    Database model for user
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    roles: str = Field(default="USER")  # Comma-separated roles
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    """
    Model for creating a new user (includes password)
    """
    password: str

class UserUpdate(SQLModel):
    """
    Model for updating user information
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None

class UserResponse(UserBase):
    """
    Model for user response (excludes sensitive data)
    """
    id: int
    roles: List[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, user: User):
        """
        Convert DB model to response model
        """
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            disabled=user.disabled,
            tenant=user.tenant,
            roles=user.roles.split(",") if user.roles else [],
            created_at=user.created_at,
            updated_at=user.updated_at
        )
