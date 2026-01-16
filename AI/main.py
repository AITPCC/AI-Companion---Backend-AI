from fastapi import FastAPI, HTTPException
from ai_service import AIService

app = FastAPI()
# Initialize the AI service once (reused across requests).
# Make sure GOOGLE_API_KEY is set in your environment.
ai_service = AIService()

@app.get("/ask", response_model=str)
def ask_gemini(inst: str):
    try:
        text = ai_service.send_message(inst)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))