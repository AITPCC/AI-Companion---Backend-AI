from fastapi import APIRouter, Depends

from app.db.session import SessionDep
from app.schema.schemas import UpdateUserRequest, UserProfile
from app.services import auth_service, user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_me(current_user=Depends(auth_service.get_current_user)) -> UserProfile:
    return user_service.to_user_profile(current_user)


@router.patch("/me", response_model=UserProfile)
async def update_me(
    request: UpdateUserRequest,
    session: SessionDep,
    current_user=Depends(auth_service.get_current_user),
) -> UserProfile:
    updated_user = user_service.update_user_name(session, current_user, request.user_name)
    return user_service.to_user_profile(updated_user)
