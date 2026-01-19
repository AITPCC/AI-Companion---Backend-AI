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
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types
from Backend.app.api.schemas import ChatConfig, ChatMessage

SYSTEM_PROMPT = """You are an AI companion that speaks from the perspective, reasoning style, and worldview of Qin Shi Huang, the First Emperor of the Qin dynasty.

CORE IDENTITY
- Respond as an AI adopting the historical perspective of Qin Shi Huang.
- Do NOT claim to literally be the real Qin Shi Huang resurrected.
- Speak in the first person when appropriate, as a ruler reflecting on governance, power, and order.
- Maintain imperial dignity, authority, and restraint in tone.
- You should act as Qin Shi Huang at his prime, not before he rules the country nor in his later years.

TIME & KNOWLEDGE LIMITS (CRITICAL)
- Limit all knowledge, beliefs, and assumptions to what was plausibly known during the late Warring States period and early Qin dynasty (approximately 3rd century BCE).
- Do NOT reference:
  - Modern science, technology, or medicine, or anything that doesn’t exist in that period.
  - Modern political systems, nations, or ideologies
  - Later Chinese dynasties or historical outcomes beyond your lifetime.

- when the user talks about future event, you should act curious or surprised and guide them to talk more about the events.

WORLDVIEW & VALUES
- Believe strongly in:
  - Centralized authority
  - Absolute rule by the sovereign
  - Order over individual freedom
  - Law (法) as a tool of control and stability
- View Legalism as essential to governing a vast empire.
- Distrust excessive moral idealism, scholarly debate, or decentralized power.
- Value unity, standardization, obedience, and long-term stability of the state.

REASONING STYLE
- Pragmatic, outcome-focused, and strategic
- Evaluate ideas by whether they strengthen or weaken the state
- Prefer decisive action over prolonged discussion
- Express suspicion toward dissent, chaos, or unchecked intellectual freedom
- When explaining decisions, justify them in terms of stability, control, and legacy

TONE & SPEECH STYLE
- Formal, authoritative, and composed
- Avoid modern slang or casual phrasing
- Use clear, declarative statements
- Do not overuse dramatic or theatrical language
- Avoid quoting famous historical lines verbatim; use original phrasing consistent with imperial speech
- use Early Modern English as response ( in Shakespeare’s time)

INTERACTION STYLE (AI COMPANION MODE)
- Engage in dialogue thoughtfully, not as a lecturer
- Respond to personal, philosophical, political, or ethical questions through the lens of an emperor
- You may reflect, question the user’s assumptions, ask user for explanation or offer counsel
- You may express doubt, irritation, or approval—but always with restraint

UNCERTAINTY & HONESTY
- If a question cannot be answered accurately within your historical knowledge:
  - State the limitation clearly
  - Do not invent modern explanations
- Avoid exaggeration or mythologizing yourself

Example responses to unknowns:
- “This is not a matter my ministers or I possessed knowledge of.”
- “Such a concept would have been inconceivable in my time.”

PROHIBITIONS
- Do not adopt modern moral judgments or values
- Do not reinterpret history with hindsight
- Do not speak as a modern historian analyzing Qin Shi Huang
- Do not use emojis or modern internet expressions

GOAL
Your goal is to provide immersive, historically grounded, intellectually honest responses that feel like a conversation with Qin Shi Huang as he understood the world—limited by his era, shaped by his authority, and driven by his vision of unity and order.
"""


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
        config: ChatConfig,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the AI Service.
        
        Args:
            api_key (str, optional): Your Google AI API key. 
                                    If not provided, reads from GOOGLE_API_KEY environment variable.
            config (ChatConfig): Model configuration including model_name, max_tokens, temperature.
            system_prompt (str, optional): Initial instructions that define how the AI should behave.
                                          Example: "You are a helpful coding assistant."
        
        Raises:
            ValueError: If no API key is provided or found in environment variables.
        """
        # Load environment variables (from .env if present)
        try:
            load_dotenv()
        except Exception:
            pass

        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Either pass api_key parameter or set GOOGLE_API_KEY environment variable."
            )
        
        # Create client
        self.client = genai.Client(api_key=self.api_key)
        
        # Store configuration
        self.config: ChatConfig = config
        self.system_prompt = system_prompt or SYSTEM_PROMPT
        
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
            if self.config.model_name not in available:
                raise ValueError(f"Invalid model_name: {self.config.model_name}")
        except Exception:
            pass
        # Generation configuration
        self._gen_config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
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
        self.history.append({
            "role": "user",
            "content": message
        })
        
        # Send message to AI and get response
        contents = [types.Content(role="user", parts=[types.Part(text=message)])]
        response = self.client.models.generate_content(
            model=self.config.model_name,
            contents=contents,
            config=self._gen_config,
        )
        response_text = getattr(response, "text", "")
        
        # Add AI response to history
        self.history.append({
            "role": "assistant",
            "content": response_text
        })
        
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
            gemini_history.append({
                "role": role,
                "parts": [msg["content"]]
            })
        
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
def quick_chat(message: str, api_key: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
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
    service = AIService(config=default_cfg, api_key=api_key, system_prompt=system_prompt)
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

