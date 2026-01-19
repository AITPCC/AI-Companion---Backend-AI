import uvicorn
from Backend.app.api.routes import app

if __name__ == "__main__":
    # Run the minimal FastAPI app
    uvicorn.run(app, host="127.0.0.1", port=8000)
