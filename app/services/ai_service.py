"""
AI Service Module
-----------------
"""

import os
from collections.abc import Iterable
from functools import lru_cache
from inspect import isawaitable
from typing import Any, List, Optional
from uuid import uuid4

import google.genai as genai
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.ai.prompts.chat_system_prompt import SYSTEM_PROMPT
from app.core.config import get_settings

_APP_NAME = "ai-companion"
_USER_ID = "prototype-client"


@lru_cache(maxsize=1)
def _resolve_api_key() -> str:
    """Resolve Google API key from settings/env for ADK runtime."""
    settings = get_settings()
    candidates = [
        getattr(settings, "google_api_key", None),
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("GEMINI_API_KEY"),
    ]
    for key in candidates:
        if key and str(key).strip():
            return str(key).strip()
    raise ValueError("Missing Google API key. Set GOOGLE_API_KEY (or GEMINI_API_KEY).")


def _ensure_adk_auth() -> None:
    """Ensure ADK/google-genai can discover API key at runtime."""
    api_key = _resolve_api_key()
    os.environ.setdefault("GOOGLE_API_KEY", api_key)
    os.environ.setdefault("GEMINI_API_KEY", api_key)


@lru_cache(maxsize=1)
def _get_agent() -> LlmAgent:
    """Create and cache a stateless ADK agent for process lifetime."""
    _ensure_adk_auth()
    settings = get_settings()
    return LlmAgent(
        name="ai_companion_agent",
        model=settings.model_name,
        instruction=SYSTEM_PROMPT,
        generate_content_config=types.GenerateContentConfig(
            temperature=settings.temperature,
            max_output_tokens=settings.max_output_tokens,
        ),
    )


def _normalize_history(history: Optional[Iterable[Any]]) -> list[tuple[str, str]]:
    """Normalize optional history items into (role, content) tuples."""
    normalized: list[tuple[str, str]] = []
    for idx, item in enumerate(history or []):
        role = getattr(item, "role", None)
        content = getattr(item, "content", None)
        if isinstance(item, dict):
            role = item.get("role", role)
            content = item.get("content", content)

        if not content:
            continue

        normalized_role = str(role or ("user" if idx % 2 == 0 else "assistant")).lower()
        if normalized_role not in {"user", "assistant", "model"}:
            normalized_role = "user"

        normalized.append((normalized_role, str(content)))

    return normalized


def _build_prompt(message: str | list[types.Content], history: Optional[Iterable[Any]]) -> str:
    """Build a single user prompt that includes optional prior history context."""
    parts: list[str] = []

    normalized_history = _normalize_history(history)
    if normalized_history:
        parts.append("Conversation history:")
        for role, content in normalized_history:
            display_role = "assistant" if role == "model" else role
            parts.append(f"- {display_role}: {content}")
        parts.append("")

    if isinstance(message, list):
        if not message:
            raise ValueError("Message list cannot be empty")

        message_texts: list[str] = []
        for content in message:
            role = getattr(content, "role", "user")
            text_parts: list[str] = []
            for part in getattr(content, "parts", []) or []:
                text = getattr(part, "text", None)
                if text:
                    text_parts.append(text)
            if text_parts:
                message_texts.append(f"{role}: {' '.join(text_parts)}")

        if not message_texts:
            raise ValueError("Message list cannot be empty")

        parts.append("Current message:")
        parts.extend(message_texts)
        return "\n".join(parts).strip()

    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    parts.append(f"Current message:\n{message.strip()}")
    return "\n".join(parts).strip()


async def ai_service(
    message: str | list[types.Content],
    history: Optional[Iterable[Any]] = None,
) -> str:
    """Run a stateless ADK LlmAgent completion for one request."""
    _ensure_adk_auth()
    session_service = InMemorySessionService()
    runner = Runner(agent=_get_agent(), app_name=_APP_NAME, session_service=session_service)

    session_id = str(uuid4())
    created_session = session_service.create_session(
        app_name=_APP_NAME,
        user_id=_USER_ID,
        session_id=session_id,
    )
    if isawaitable(created_session):
        await created_session

    new_message = types.Content(
        role="user",
        parts=[types.Part(text=_build_prompt(message=message, history=history))],
    )

    final_text = ""
    async for event in runner.run_async(
        user_id=_USER_ID,
        session_id=session_id,
        new_message=new_message,
    ):
        if not event.is_final_response() or not event.content:
            continue
        text_chunks = [
            part.text for part in event.content.parts if getattr(part, "text", None)
        ]
        if text_chunks:
            final_text = "\n".join(text_chunks).strip()

    return final_text


def list_available_models(api_key: Optional[str] = None) -> List[str]:
    """List all available Gemini models for the provided (or configured) API key."""
    resolved_api_key = api_key or _resolve_api_key()
    client = genai.Client(api_key=resolved_api_key)
    return [m.name for m in client.models.list()]
