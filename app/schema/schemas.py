"""
Schemas for chat request and response using Pydantic
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing import Annotated, List, Optional


class ChatMessage(BaseModel):
    """
    Represents a single message in the chat history
    """

    role: str = Field(
        default="user",
        description="The message role. Use 'user', 'assistant', or 'model'.",
    )
    content: str = Field(
        ..., min_length=1, max_length=4000, description="The actual text content of the message"
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

    message: str = Field(..., min_length=1, max_length=4000, description="The message sent by the user")
    history: Optional[List[ChatMessage]] = Field(
        default_factory=list, max_length=20, description="History messages"
    )
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


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    user_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ] = Field(..., description="Display name")


class UpdateUserRequest(BaseModel):
    user_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ] = Field(..., description="New display name")


class UserProfile(BaseModel):
    user_id: int = Field(..., description="Unique user identifier")
    user_name: str = Field(..., description="Display name")
    email: EmailStr = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


__all__ = [
    "ChatMessage",
    "ChatConfig",
    "ChatRequest",
    "ChatResponse",
    "RegisterRequest",
    "UpdateUserRequest",
    "UserProfile",
    "LoginRequest",
    "LoginResponse",
]
