"""
AI Service Module
-----------------
This module provides a clean, reusable interface for interacting with Google's Gemini AI.
It's designed to be easily plugged into any project that needs AI capabilities.

Key Features:
- System prompt support (defines AI personality/behavior)
- Conversation history management (maintains context across messages)
- Simple, encapsulated design (easy to use and maintain)
"""

import os
from typing import Any, Dict, Iterable, List, Optional, Union

import google.genai as genai
from google.genai import types
from app.schema.schemas import ChatConfig, ChatMessage
from app.ai.prompts.chat_system_prompt import SYSTEM_PROMPT
from app.core.config import get_settings


class AIService:
    """
    A service class for interacting with Google's Gemini AI.

    This class encapsulates all AI functionality in one place, making it easy
    to use AI capabilities in your projects.

    Attributes:
        model_name (str): The Gemini model to use (default: "gemini-1.5-flash")
        system_prompt (str): The initial instructions that define the AI's behavior
        history (List[Dict]): The conversation history between user and AI
    """

    def __init__(
        self,
    ):
        """
        Initialize the AI Service.

        Args:
            config (ChatConfig): Model configuration including mode, model_name, temperature.
        """
        self.api_key = get_settings().google_api_key
        self.model_name = get_settings().model_name
        self.temperature = get_settings().temperature
        self.max_output_tokens = get_settings().max_output_tokens
        # Create client
        self.client = genai.Client(api_key=self.api_key)

        # Store configuration
        self.system_prompt = SYSTEM_PROMPT

        # Initialize conversation history
        # History is a list of dictionaries with 'role' and 'content' keys
        # Example: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]
        self.history: List[Dict[str, str]] = []

        # Initialize the model
        self._initialize_model()

    def _initialize_model(self):
        """Prepare generation config."""
        # Optional validation
        try:
            available = [m.name for m in self.client.models.list()]
            if self.model_name not in available:
                raise ValueError(f"Invalid model_name: {self.model_name}")
        except Exception:
            pass
        # Generation configuration
        self._gen_config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )

    def send_message(self, message: str) -> str:
        """
        Send a message to the AI and get a response.

        This method automatically maintains the conversation history, so the AI
        remembers what was said earlier in the conversation.

        Args:
            message (str): The message/question you want to send to the AI

        Returns:
            str: The AI's response

        Example:
            >>> service = AIService()
            >>> response = service.send_message("What is Python?")
            >>> print(response)
            Python is a high-level programming language...
        """
        # Add user message to history
        self.history.append({"role": "user", "content": message})

        # Send message to AI and get response
        contents = [types.Content(role="user", parts=[types.Part(text=message)])]
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=self._gen_config,
        )
        response_text = getattr(response, "text", "")

        # Add AI response to history
        self.history.append({"role": "assistant", "content": response_text})

        return response_text

    def send_message_with_config(
        self,
        message: ChatMessage,
        history: Optional[Iterable[ChatMessage]] = None,
        config: Optional[ChatConfig] = None,
    ) -> str:
        """
        Send a message using config values and an optional history list.

        This aligns with the fields in schemas.py:
        - config.model_name
        - config.max_tokens
        - config.temperature
        - message: ChatMessage
        - history: List[ChatMessage] (content only)
        """
        if config is not None:
            self.update_config(config)

        if history is not None:
            self.load_history(self._normalize_history(history))

        return self.send_message(message.content)

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the full conversation history.

        Returns:
            List[Dict[str, str]]: List of messages with 'role' and 'content' keys

        Example:
            >>> history = service.get_history()
            >>> for msg in history:
            ...     print(f"{msg['role']}: {msg['content']}")
        """
        return self.history.copy()

    def clear_history(self):
        """
        Clear the conversation history and start fresh.

        This is useful when you want to start a new conversation without
        the AI remembering previous messages.

        Example:
            >>> service.send_message("My name is John")
            >>> service.clear_history()
            >>> service.send_message("What's my name?")
            # AI won't remember "John" because we cleared the history
        """
        self.history = []

    def set_system_prompt(self, new_prompt: str):
        """
        Change the system prompt and reinitialize the model.

        The system prompt defines how the AI should behave. Changing it
        will restart the conversation with the new personality/instructions.

        Args:
            new_prompt (str): The new system prompt/instructions

        Example:
            >>> service = AIService(system_prompt="You are a helpful assistant")
            >>> service.set_system_prompt("You are a Python expert who gives concise answers")
            # Now the AI will behave as a Python expert
        """
        self.system_prompt = new_prompt
        self.clear_history()
        self._initialize_model()

    def update_config(self, config: Union[ChatConfig, Dict[str, Any]]):
        """
        Update configuration using a config object or dict.

        Expected fields: model_name, max_tokens, temperature.
        """
        model_name = getattr(config, "model_name", None)
        max_tokens = getattr(config, "max_tokens", None)
        temperature = getattr(config, "temperature", None)
        if isinstance(config, dict):
            model_name = config.get("model_name", model_name)
            max_tokens = config.get("max_tokens", max_tokens)
            temperature = config.get("temperature", temperature)

        if model_name:
            self.config.model_name = model_name
        if max_tokens is not None:
            self.config.max_tokens = max_tokens
        if temperature is not None:
            self.config.temperature = temperature

        # Reinitialize to apply model/config changes.
        self._initialize_model()

    def load_history(self, history: List[Dict[str, str]]):
        """
        Load an existing conversation history.

        This is useful for:
        - Restoring a previous conversation
        - Starting with pre-loaded context
        - Testing specific conversation states

        Args:
            history (List[Dict[str, str]]): List of messages to load
                Each message should have 'role' (either 'user' or 'assistant')
                and 'content' (the message text)

        Example:
            >>> old_history = [
            ...     {"role": "user", "content": "Hello"},
            ...     {"role": "assistant", "content": "Hi! How can I help?"}
            ... ]
            >>> service.load_history(old_history)
            >>> # Now the AI remembers this conversation
        """
        self.history = history.copy()

        # Convert our history format to Gemini's format
        gemini_history = []
        for msg in self.history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Restart chat with the loaded history
        self.chat_session = self.model.start_chat(history=gemini_history)

    def _normalize_history(self, history: Iterable[Any]) -> List[Dict[str, str]]:
        """
        Normalize a history list into [{"role": "...", "content": "..."}] format.

        Supports:
        - Dicts with 'role' + 'content'
        - Objects with a 'content' attribute (from schemas.ChatMessage)

        If role is missing, messages alternate between user/model starting with user.
        """
        normalized: List[Dict[str, str]] = []
        fallback_role = "user"

        for msg in history:
            if isinstance(msg, dict):
                content = msg.get("content")
                role = msg.get("role", fallback_role)
            else:
                content = getattr(msg, "content", None)
                role = getattr(msg, "role", fallback_role)

            if not content:
                continue

            normalized.append({"role": role, "content": content})

            # Alternate role if role was not explicitly set
            if "role" not in (msg if isinstance(msg, dict) else {}):
                fallback_role = "assistant" if fallback_role == "user" else "user"

        return normalized


# Singleton instance of the AIService
ai_service = AIService()


def list_available_models(api_key: Optional[str] = None) -> List[str]:
    """
    List all available Gemini models for your API key.

    This is helpful to see which models you can use.

    Args:
        api_key (str, optional): Your API key (or use GOOGLE_API_KEY env variable)

    Returns:
        List[str]: List of available model names

    Example:
        >>> models = list_available_models()
        >>> print(models)
        ['gemini-pro', 'gemini-1.5-pro', ...]
    """
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No API key provided")

    client = genai.Client(api_key=api_key)
    models = [m.name for m in client.models.list()]
    return models


# Convenience function for quick usage without creating a class instance
def quick_chat(
    message: str, api_key: Optional[str] = None, system_prompt: Optional[str] = None
) -> str:
    """
    Quick way to get a single AI response without managing a service instance.

    This is useful for one-off questions where you don't need conversation history.

    Args:
        message (str): Your message/question
        api_key (str, optional): Your API key (or use GOOGLE_API_KEY env variable)
        system_prompt (str, optional): System instructions for the AI

    Returns:
        str: The AI's response

    Example:
        >>> response = quick_chat("What is 2+2?")
        >>> print(response)
        4
    """
    # Use default ChatConfig for quick usage
    default_cfg = ChatConfig()
    service = AIService(
        config=default_cfg, api_key=api_key, system_prompt=system_prompt
    )
    return service.send_message(message)


if __name__ == "__main__":
    # This code only runs when you execute this file directly
    # It won't run when you import this module into another file

    print("AI Service Module")
    print("=" * 50)
    print("\nThis module is meant to be imported and used in other files.")
    print("\nExample usage:")
    print("    from ai_service import AIService")
    print("    service = AIService()")
    print("    response = service.send_message('Hello!')")
    print("\nRun test.py to see full examples!")
