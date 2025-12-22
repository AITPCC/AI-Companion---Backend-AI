"""
FastAPI Application - AI Companion Backend
Integrates with Gemini AI through the AI module
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# Add parent directory to path to import AI module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI import GeminiClient

# Initialize FastAPI app
app = FastAPI(
    title="AI Companion - Backend API",
    description="FastAPI backend integrated with Google's Gemini AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
try:
    gemini_client = GeminiClient()
except Exception as e:
    print(f"Warning: Failed to initialize Gemini client: {e}")
    gemini_client = None


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for simple chat"""
    prompt: str
    model: Optional[str] = "gemini-2.5-flash"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class ChatResponse(BaseModel):
    """Response model for simple chat"""
    response: str
    model: str


class ChatHistoryMessage(BaseModel):
    """Individual message in chat history"""
    role: str  # 'user' or 'model'
    content: str


class ChatConversationRequest(BaseModel):
    """Request model for conversation with history"""
    message: str
    history: Optional[List[ChatHistoryMessage]] = []
    model: Optional[str] = "gemini-2.5-flash"


class ChatConversationResponse(BaseModel):
    """Response model for conversation"""
    response: str
    model: str
    history: List[ChatHistoryMessage]


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - provides API information"""
    return {
        "message": "Welcome to AI Companion Backend API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "Send a single prompt to Gemini AI",
            "/chat/conversation": "Have a conversation with context",
            "/models": "List available Gemini models",
            "/health": "Check API health status"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the API and Gemini connection are healthy"""
    try:
        if not gemini_client:
            raise Exception("Gemini client not initialized")
        
        # Try to list models to verify API connection
        gemini_client.list_available_models()
        
        return {
            "status": "healthy",
            "gemini_api": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )


# List available models
@app.get("/models")
async def list_models():
    """Get list of available Gemini models"""
    try:
        if not gemini_client:
            raise HTTPException(
                status_code=503,
                detail="Gemini client not initialized. Check API key configuration."
            )
        
        models = gemini_client.list_available_models()
        return {"models": models, "count": len(models)}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching models: {str(e)}"
        )


# Simple chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate a response from Gemini AI for a single prompt
    
    Args:
        request: ChatRequest with prompt and optional parameters
        
    Returns:
        ChatResponse with generated text
    """
    try:
        if not gemini_client:
            raise HTTPException(
                status_code=503,
                detail="Gemini client not initialized. Check API key configuration."
            )
        
        # Call Gemini API through the AI module
        response_text = gemini_client.generate_content(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens
        )
        
        return ChatResponse(
            response=response_text,
            model=request.model
        )
        
    except ValueError as e:
        # Handle validation errors (e.g., content blocked)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Error in /chat endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


# Conversation endpoint with history
@app.post("/chat/conversation", response_model=ChatConversationResponse)
async def chat_conversation(request: ChatConversationRequest):
    """
    Have a conversation with Gemini AI maintaining context/history
    
    Args:
        request: ChatConversationRequest with message, history, and model
        
    Returns:
        ChatConversationResponse with response and updated history
    """
    try:
        if not gemini_client:
            raise HTTPException(
                status_code=503,
                detail="Gemini client not initialized. Check API key configuration."
            )
        
        # Convert Pydantic models to dicts for the AI module
        history_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]
        
        # Call Gemini API through the AI module
        result = gemini_client.chat_with_history(
            message=request.message,
            history=history_dicts,
            model=request.model
        )
        
        # Convert response back to Pydantic models
        history_models = [
            ChatHistoryMessage(role=msg["role"], content=msg["content"])
            for msg in result["history"]
        ]
        
        return ChatConversationResponse(
            response=result["response"],
            model=request.model,
            history=history_models
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Error in /chat/conversation endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error in conversation: {str(e)}"
        )


# Streaming endpoint (for future enhancement)
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Generate streaming response from Gemini AI
    Note: This currently returns the full response. True streaming with
    Server-Sent Events can be implemented in future versions.
    """
    try:
        if not gemini_client:
            raise HTTPException(
                status_code=503,
                detail="Gemini client not initialized. Check API key configuration."
            )
        
        # Collect streaming chunks
        full_response = ""
        for chunk in gemini_client.generate_stream(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens
        ):
            full_response += chunk
        
        return {
            "response": full_response,
            "model": request.model,
            "note": "Full streaming with SSE will be implemented in future versions"
        }
        
    except Exception as e:
        import traceback
        print(f"Error in /chat/stream endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error in streaming: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

