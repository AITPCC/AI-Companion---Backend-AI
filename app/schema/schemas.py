"""
Schemas for chat request and response using Pydantic
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    """
    Represents a single message in the chat history
    """

    content: str = Field(
        ..., min_length=1, description="The actual text content of the message"
    )


class ChatConfig(BaseModel):
    """
    Configuration for the AI Model
    """

    model_name: str = Field(
        default="gemini-1.5-flash", description="The model name to be used"
    )
    max_tokens: int = Field(
        default=150, ge=1, le=1145, description="Rate limit on the number of tokens"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Creativity level. 0.0 is deterministic, 1.0 is creative",
    )


class ChatRequest(BaseModel):
    """
    Represents a chat request from the user
    """

    message: str = Field(..., min_length=1, description="The message sent by the user")
    history: List[ChatMessage] = Field(default=[], description="History messages")
    config: ChatConfig = Field(..., description="Configs for the AI Model")


class ChatResponse(BaseModel):
    """
    Represents the response from the AI Model
    """

    status: int = Field(..., description="HTTP Status Code")
    content: Optional[str] = Field(
        default=None, description="The AI generated reply. None if an error occured."
    )
    error: Optional[str] = Field(
        default=None, description="Error message. None on success."
    )


__all__ = ["ChatMessage", "ChatConfig", "ChatRequest", "ChatResponse"]
