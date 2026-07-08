from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.db.session import SessionDep
from app.schema.schemas import LoginRequest, LoginResponse, RegisterRequest, UserProfile
from app.services import auth_service, user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserProfile)
async def register(request: RegisterRequest, session: SessionDep) -> UserProfile:
    if user_service.find_by_email(session, request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    password_hash = auth_service.hash_password(request.password)
    user = user_service.create_user(
        session,
        user_name=request.user_name,
        email=request.email,
        password_hash=password_hash,
    )

    return UserProfile(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.user_email,
        created_at=user.created_at,
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, session: SessionDep) -> LoginResponse | JSONResponse:
    user = user_service.find_by_email(session, request.email)
    invalid_credentials = user is None or not auth_service.verify_password(
        request.password,
        user.password_hash if user else "",
    )

    if invalid_credentials:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": 400, "error": "Invalid email or password"},
        )

    return LoginResponse(
        access_token=auth_service.create_access_token(user.user_id),
        token_type="bearer",
    )
