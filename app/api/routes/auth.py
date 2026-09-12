from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.client_ip import client_ip
from app.core.config import get_settings
from app.db.session import SessionDep
from app.schema.schemas import LoginRequest, LoginResponse, RegisterRequest, UserProfile
from app.services import auth_service, quota_service, user_service
from app.services.quota_service import Budget, identity_key

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserProfile
)
def register(
    request: RegisterRequest, http_request: Request, session: SessionDep
) -> UserProfile:
    quota_service.reserve(
        Budget(
            "register",
            client_ip(http_request),
            "register",
            settings.register_limit,
            settings.register_window_seconds,
        )
    )

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
def login(
    request: LoginRequest, http_request: Request, session: SessionDep
) -> LoginResponse | JSONResponse:
    reservation = quota_service.reserve(
        Budget(
            "login",
            identity_key(request.email.strip().lower(), client_ip(http_request)),
            "login",
            settings.login_limit,
            settings.login_window_seconds,
        )
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

    user_id = user.user_id
    # Release the read transaction before the refund opens its own connection.
    session.rollback()
    quota_service.refund(reservation)
    return LoginResponse(
        access_token=auth_service.create_access_token(user_id),
        token_type="bearer",
    )


@router.post(
    "/guest-session", status_code=status.HTTP_201_CREATED, response_model=LoginResponse
)
def guest_session() -> LoginResponse:
    return LoginResponse(
        access_token=auth_service.create_guest_token(),
        token_type="bearer",
    )
