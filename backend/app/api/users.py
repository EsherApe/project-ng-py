from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.app.models.user import User, UserCreate, UserUpdate, UserResponse
from backend.app.core.security import get_password_hash
from backend.app.db.database import get_db
from backend.app.core.dependencies import get_current_active_superuser, get_current_active_user, check_roles

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(check_roles(["ADMIN"])),
) -> Any:
    """
    Retrieve users (admin only)
    """
    # Filter users by tenant for multi-tenant support
    users = db.exec(
        select(User)
        .where(User.tenant == current_user.tenant)
        .offset(skip)
        .limit(limit)
    ).all()

    return [UserResponse.from_orm(user) for user in users]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_in: UserCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_roles(["ADMIN"])),
) -> Any:
    """
    Create new user (admin only)
    """
    # Check if username exists in the same tenant
    user = db.exec(
        select(User)
        .where(User.username == user_in.username, User.tenant == current_user.tenant)
    ).first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists in the same tenant
    user = db.exec(
        select(User)
        .where(User.email == user_in.email, User.tenant == current_user.tenant)
    ).first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user with current user's tenant
    db_user = User(
        **user_in.dict(exclude={"password"}),
        hashed_password=get_password_hash(user_in.password),
        tenant=current_user.tenant
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse.from_orm(db_user)

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific user by id
    """
    # Users can only see their own profile unless they're an admin
    if current_user.id != user_id and "ADMIN" not in current_user.roles.split(","):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get user and verify tenant for multi-tenant security
    user = db.exec(
        select(User)
        .where(User.id == user_id, User.tenant == current_user.tenant)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.from_orm(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_in: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a user
    """
    # Users can only update their own profile unless they're an admin
    if current_user.id != user_id and "ADMIN" not in current_user.roles.split(","):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get user and verify tenant
    user = db.exec(
        select(User)
        .where(User.id == user_id, User.tenant == current_user.tenant)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update user fields if provided
    update_data = user_in.dict(exclude_unset=True)

    # Hash the password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    # Update timestamp
    user.updated_at = datetime.utcnow()

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_roles(["ADMIN"])),
) -> None:
    """
    Delete a user (admin only)
    """
    # Get user and verify tenant
    user = db.exec(
        select(User)
        .where(User.id == user_id, User.tenant == current_user.tenant)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own user account",
        )

    db.delete(user)
    db.commit()

@router.put("/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
        user_id: int,
        roles: List[str],
        db: Session = Depends(get_db),
        current_user: User = Depends(check_roles(["ADMIN"])),
) -> Any:
    """
    Update user roles (admin only)
    """
    # Get user and verify tenant
    user = db.exec(
        select(User)
        .where(User.id == user_id, User.tenant == current_user.tenant)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update roles
    user.roles = ",".join(roles)
    user.updated_at = datetime.utcnow()

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)