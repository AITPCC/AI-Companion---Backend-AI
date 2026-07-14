from fastapi import APIRouter, Depends

from app.schema.schemas import UserProfile
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_me(current_user=Depends(auth_service.get_current_user)) -> UserProfile:
    return UserProfile(
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        email=current_user.user_email,
        created_at=current_user.created_at,
    )
