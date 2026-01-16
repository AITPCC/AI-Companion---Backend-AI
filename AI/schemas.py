from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ChatMessage(BaseModel):
    content: str = Field(
            ...,
            min_length=1,
            description="The actual text content of the message"
            )

class ChatConfig(BaseModel):
    model_name: str = Literal(
            default="gemini-2.5-flash",
            description="The model name to be used"
            )
    max_tokens: int = Field(
            default=150,
            ge=1,
            le=1145,
            description="Rate limit on the number of tokens"
            )
    temperature: float = Field(
            default=0.7,
            le=0.,
            ge=1.,
            description="Creativity level. 0.0 is deterministic, 1.0 is creative"
            )

class ChatRequest(BaseModel):
    message: str = Field(
            ...,
            min_length=1,
            description="The message sent by the user"
            )
    history: List[ChatMessage] = Field(
            default=[],
            description="History messages"
            )
    config: ChatConfig = Field(
            ...,
            description="Configs for the AI Model"
            )

class ChatResponse(BaseModel):
    status: int = Field(
            ...,
            description="HTTP Status Code"
            )
    content: Optional[str] = Field(
            default=None,
            description="The AI generated reply. None if an error occured."
            )
    error: Optional[str] = Field(
            default=None,
            description="Error message. None on success."