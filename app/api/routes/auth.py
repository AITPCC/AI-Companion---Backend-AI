from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.session import SessionDep
from app.schema.schemas import LoginRequest, LoginResponse, RegisterRequest, UserProfile
from app.services import auth_service, quota_service, user_service

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()


def _client_ip(http_request: Request) -> str:
    return http_request.client.host if http_request.client else "unknown"


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserProfile)
async def register(request: RegisterRequest, http_request: Request, session: SessionDep) -> UserProfile:
    allowed = quota_service.check_and_increment(
        session,
        "register",
        _client_ip(http_request),
        "register",
        settings.register_limit,
        settings.register_window_seconds,
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

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

    return user_service.to_user_profile(user)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, http_request: Request, session: SessionDep) -> LoginResponse | JSONResponse:
    # Count every attempt so a blocked caller never reaches password verification.
    actor_id = quota_service.hash_key(
        request.email.strip().lower(), _client_ip(http_request)
    )
    allowed = quota_service.check_and_increment(
        session,
        "login",
        actor_id,
        "login",
        settings.login_limit,
        settings.login_window_seconds,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )

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


@router.post("/guest-session", status_code=status.HTTP_201_CREATED, response_model=LoginResponse)
async def guest_session() -> LoginResponse:
    return LoginResponse(
        access_token=auth_service.create_guest_token(),
        token_type="bearer",
    )
