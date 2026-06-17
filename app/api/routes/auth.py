from fastapi import APIRouter, HTTPException, status

from app.schema.schemas import RegisterRequest, UserProfile
from app.services import auth_service, user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserProfile)
async def register(request: RegisterRequest) -> UserProfile:
    if user_service.find_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    password_hash = auth_service.hash_password(request.password)
    user = user_service.create_user(
        user_name=request.user_name,
        email=request.email,
        password_hash=password_hash,
    )

    return UserProfile(
        user_id=user["user_id"],
        user_name=user["user_name"],
        email=user["user_email"],
        created_at=user["created_at"],
    )
