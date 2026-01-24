from dotenv import dotenv_values
import google.genai as genai

class GeminiClient:
    def __init__(self):
        config = dotenv_values(".env")
        api_key = config["GEMINI_APIKEY"]

        self.client = genai.Client(api_key=api_key)

    def call(self, instruction: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=instruction
        )
        return response.text
