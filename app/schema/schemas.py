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

    mode: Optional[str] = Field(
        default="history_figure", description="The AI Companion mode to apply"
    )


class ChatRequest(BaseModel):
    """
    Represents a chat request from the user
    """

    message: str = Field(..., min_length=1, description="The message sent by the user")
    history: Optional[List[ChatMessage]] = Field(default=[], description="History messages")
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
