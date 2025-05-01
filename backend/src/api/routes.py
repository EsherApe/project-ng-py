from fastapi import APIRouter, HTTPException
from models.user import User
from models.response import SuccessResponse

router = APIRouter()

FAKE_USERS_DB = {
    1: {
        "id": 1,
        "username": "andrii",
        "full_name": "Andrii Bazylskyi",
        "email": "andrii@example.com",
        "disabled": False,
        "tenant": "acme",
        "role": "admin"
    }
}

@router.get("/user/{user_id}", response_model=SuccessResponse)
async def get_user_by_id(user_id: int):
    user = FAKE_USERS_DB.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "code": 404,
                "message": "User not found"
            }
        )

    return SuccessResponse(data=user)