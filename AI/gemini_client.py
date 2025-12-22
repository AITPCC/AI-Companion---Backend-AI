"""
Gemini API Client
This module encapsulates all Gemini AI API calls
"""
import google.generativeai as genai
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiClient:
    """Client for interacting with Google's Gemini AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client
        
        Args:
            api_key: Gemini API key. If not provided, will use GEMINI_API_KEY from environment
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please provide it or set in environment variables.")
        
        genai.configure(api_key=self.api_key)
        self.default_model = "gemini-2.5-flash"
    
    def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1000
    ) -> str:
        """
        Generate content using Gemini AI
        
        Args:
            prompt: The input prompt/question
            model: Model name (defaults to gemini-2.5-flash)
            temperature: Temperature for generation (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        try:
            model_name = model or self.default_model
            gemini_model = genai.GenerativeModel(model_name)
            
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
            )
            
            if not response.text:
                # Check if content was blocked
                if hasattr(response, 'prompt_feedback'):
                    raise ValueError(f"Content blocked: {response.prompt_feedback}")
                raise ValueError("No response text generated")
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Error generating content with Gemini: {str(e)}")
    
    def chat_with_history(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None
    ) -> Dict:
        """
        Have a conversation with context/history
        
        Args:
            message: The new message to send
            history: List of previous messages [{"role": "user"/"model", "content": "..."}]
            model: Model name (defaults to gemini-2.5-flash)
            
        Returns:
            Dict with 'response' and updated 'history'
            
        Raises:
            Exception: If chat fails
        """
        try:
            model_name = model or self.default_model
            gemini_model = genai.GenerativeModel(model_name)
            
            # Convert history to Gemini format
            gemini_history = []
            if history:
                for msg in history:
                    gemini_history.append({
                        "role": msg["role"],
                        "parts": [msg["content"]]
                    })
            
            # Start chat with history
            chat = gemini_model.start_chat(history=gemini_history)
            
            # Send message and get response
            response = chat.send_message(message)
            
            if not response.text:
                raise ValueError("No response text generated")
            
            # Update history
            updated_history = history.copy() if history else []
            updated_history.append({"role": "user", "content": message})
            updated_history.append({"role": "model", "content": response.text})
            
            return {
                "response": response.text,
                "history": updated_history
            }
            
        except Exception as e:
            raise Exception(f"Error in chat conversation: {str(e)}")
    
    def list_available_models(self) -> List[Dict[str, any]]:
        """
        List all available Gemini models
        
        Returns:
            List of model information dictionaries
        """
        try:
            models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append({
                        "name": model.name,
                        "display_name": model.display_name,
                        "description": model.description,
                        "input_token_limit": model.input_token_limit,
                        "output_token_limit": model.output_token_limit,
                    })
            return models
        except Exception as e:
            raise Exception(f"Error listing models: {str(e)}")
    
    def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1000
    ):
        """
        Generate content with streaming (yields chunks as they arrive)
        
        Args:
            prompt: The input prompt/question
            model: Model name (defaults to gemini-2.5-flash)
            temperature: Temperature for generation (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            
        Yields:
            Text chunks as they are generated
        """
        try:
            model_name = model or self.default_model
            gemini_model = genai.GenerativeModel(model_name)
            
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise Exception(f"Error in streaming generation: {str(e)}")

