from google.genai import types
from fastapi import APIRouter, status

from app.schema.schemas import ChatRequest, ChatResponse
from app.services.ai_service import ai_service
from app.logger import get_logger

logger = get_logger(name=__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/completions", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not request.message or not request.message.strip():
        return ChatResponse(
            status=status.HTTP_400_BAD_REQUEST,
            content=None,
            error="Message cannot be empty",
        )

    try:
        history = request.history or []
        combined = [
            types.Content(
                role="model" if msg.role in ["assistant", "model"] else "user",
                parts=[types.Part(text=msg.content)],
            )
            for msg in history
        ]
        combined.append(
            types.Content(role="user", parts=[types.Part(text=request.message)])
        )
        reply = ai_service.send_message(combined)
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
