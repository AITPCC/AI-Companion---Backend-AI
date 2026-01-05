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
from typing import List, Dict, Optional
import google.generativeai as genai


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
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the AI Service.
        
        Args:
            api_key (str, optional): Your Google AI API key. 
                                    If not provided, reads from GOOGLE_API_KEY environment variable.
            model_name (str): Which Gemini model to use. Default is "gemini-2.5-flash"
                            Common options: "gemini-2.5-flash", "gemini-pro", "gemini-1.5-pro"
            system_prompt (str, optional): Initial instructions that define how the AI should behave.
                                          Example: "You are a helpful coding assistant."
        
        Raises:
            ValueError: If no API key is provided or found in environment variables.
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Either pass api_key parameter or set GOOGLE_API_KEY environment variable."
            )
        
        # Configure the Google AI SDK
        genai.configure(api_key=self.api_key)
        
        # Store configuration
        self.model_name = model_name
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        
        # Initialize conversation history
        # History is a list of dictionaries with 'role' and 'content' keys
        # Example: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]
        self.history: List[Dict[str, str]] = []
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """
        Internal method to initialize the Gemini model with the system prompt.
        
        This is called automatically during __init__.
        """
        # Create the model with system instructions
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt
        )
        
        # Start a chat session (this allows us to maintain conversation history)
        self.chat_session = self.model.start_chat(history=[])
    
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
        response = self.chat_session.send_message(message)
        
        # Extract the text from the response
        response_text = response.text
        
        # Add AI response to history
        self.history.append({
            "role": "assistant",
            "content": response_text
        })
        
        return response_text
    
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
        # Restart the chat session
        self.chat_session = self.model.start_chat(history=[])
    
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
    
    genai.configure(api_key=api_key)
    
    models = []
    for model in genai.list_models():
        # Only include models that support generateContent
        if 'generateContent' in model.supported_generation_methods:
            models.append(model.name)
    
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
    service = AIService(api_key=api_key, system_prompt=system_prompt)
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

