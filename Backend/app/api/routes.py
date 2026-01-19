from fastapi import FastAPI, status
from Backend.app.api.schemas import ChatRequest, ChatResponse
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not request.message or not request.message.strip():
        return ChatResponse(status=status.HTTP_400_BAD_REQUEST, content=None, error="Message cannot be empty")

    try:
        from AI.ai_service import AIService
        service = AIService(config=request.config)
        reply = service.send_message(request.message)
        return ChatResponse(status=status.HTTP_200_OK, content=reply, error=None)
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return ChatResponse(status=status.HTTP_400_BAD_REQUEST, content=None, error=str(e))
    except Exception as e:
        logger.error(f"AI error: {e}")
        return ChatResponse(status=status.HTTP_503_SERVICE_UNAVAILABLE, content=None, error=str(e))

