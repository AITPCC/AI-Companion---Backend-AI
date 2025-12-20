from fastapi import FastAPI, HTTPException
from AI import GeminiClient

app = FastAPI()
client = GeminiClient()

@app.get("/ask", response_model=str)
def ask_gemini(inst: str):
    try:
        text = client.call(inst)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
