from fastapi import APIRouter, Depends, Request, status

from app.api.client_ip import client_ip
from app.api.dependencies import Actor, current_actor
from app.core.config import get_settings
from app.logger import get_logger
from app.schema.schemas import ChatRequest, ChatResponse
from app.services import quota_service
from app.services.ai_service import ai_service
from app.services.quota_service import Budget

logger = get_logger(name=__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

settings = get_settings()


@router.post("/completions", response_model=ChatResponse)
async def chat(
    request: ChatRequest, http_request: Request, actor: Actor = Depends(current_actor)
) -> ChatResponse:
    if not request.message or not request.message.strip():
        return ChatResponse(
            status=status.HTTP_400_BAD_REQUEST,
            content=None,
            error="Message cannot be empty",
        )

    if actor.kind == "guest":
        # This budget survives minting a new guest token.
        await quota_service.reserve_async(
            Budget(
                "guest_ip",
                client_ip(http_request),
                "chat",
                settings.guest_source_limit,
                settings.chat_window_seconds,
            )
        )
    limit = (
        settings.chat_guest_limit if actor.kind == "guest" else settings.chat_user_limit
    )
    await quota_service.reserve_async(
        Budget(
            actor.kind,
            actor.id,
            "chat",
            limit,
            settings.chat_window_seconds,
        )
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
