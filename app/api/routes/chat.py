from fastapi import APIRouter, status

from app.schema.schemas import ChatRequest, ChatResponse
from app.ai.ai_service import AIService
from app.logger import get_logger

logger = get_logger(name=__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not request.message or not request.message.strip():
        return ChatResponse(
            status=status.HTTP_400_BAD_REQUEST,
            content=None,
            error="Message cannot be empty",
        )

    try:
        service = AIService(config=request.config)
        reply = service.send_message(request.message)
        return ChatResponse(status=status.HTTP_200_OK, content=reply, error=None)
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return ChatResponse(
            status=status.HTTP_400_BAD_REQUEST, content=None, error=str(e)
        )
    except Exception as e:
        logger.error(f"AI error: {e}")
        return ChatResponse(
            status=status.HTTP_503_SERVICE_UNAVAILABLE, content=None, error=str(e)
        )
