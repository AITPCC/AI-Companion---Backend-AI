from fastapi import APIRouter, HTTPException, Request, status, Depends

from app.api.dependencies import Actor, current_actor

from app.db.session import SessionDep
from app.schema.schemas import ChatRequest, ChatResponse
from app.services.ai_service import ai_service
from app.logger import get_logger
from app.services import quota_service
from app.core.config import get_settings

logger = get_logger(name=__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

settings = get_settings()


@router.post("/completions", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    http_request: Request,
    session: SessionDep,
    actor: Actor = Depends(current_actor)) -> ChatResponse:
    limit = settings.chat_guest_limit if actor.kind == "guest" else settings.chat_user_limit
    actor_id = actor.id
    if actor.kind == "guest":
        # A new guest token should not create a fresh quota.
        actor_id = http_request.client.host if http_request.client else "unknown"
    allowed = quota_service.check_and_increment(
        session, actor.kind, actor_id, "chat", limit, settings.chat_window_seconds
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
    if not request.message or not request.message.strip():
        return ChatResponse(
            status=status.HTTP_400_BAD_REQUEST,
            content=None,
            error="Message cannot be empty",
        )

    try:
        reply = await ai_service(
            message=request.message,
            history=request.history,
        )
        return ChatResponse(status=status.HTTP_200_OK, content=reply, error=None)
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return ChatResponse(
            status=status.HTTP_400_BAD_REQUEST, content=None, error=str(e)
        )
    except Exception:
        logger.exception("AI request failed")
        return ChatResponse(
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=None,
            error="The chat service is temporarily unavailable",
        )
