from fastapi import APIRouter, Depends

from app.schema.schemas import UserProfile
from app.services import auth_service, user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_me(current_user=Depends(auth_service.get_current_user)) -> UserProfile:
    return user_service.to_user_profile(current_user)
