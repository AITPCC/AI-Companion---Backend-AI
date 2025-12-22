# AI Companion - Backend AI

FastAPI backend integrated with Google's Gemini AI API.

## 📁 Project Structure

```
AI-companion---Backend-AI/
├── AI/                          # Gemini API integration module
│   ├── __init__.py
│   ├── gemini_client.py         # Main Gemini client class
│   └── config.py                # AI module configuration
├── Backend/                     # FastAPI application
│   ├── __init__.py
│   └── main.py                  # FastAPI app with endpoints
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Features

- **Modular Architecture**: Separated AI logic (in `AI/`) from API logic (in `Backend/`)
- **Multiple Endpoints**:
  - `/chat` - Simple single-turn conversations
  - `/chat/conversation` - Multi-turn conversations with history
  - `/chat/stream` - Streaming responses (experimental)
  - `/models` - List available Gemini models
  - `/health` - Health check endpoint
- **Interactive API Docs**: Auto-generated Swagger UI at `/docs`
- **Error Handling**: Comprehensive error handling with detailed messages
- **CORS Enabled**: Ready for frontend integration

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AITPCC/AI-companion---Backend-AI.git
   cd AI-companion---Backend-AI
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_actual_api_key_here
   ```

## 🏃 Running the Application

### Option 1: Run directly with Python
```bash
cd Backend
python main.py
```

### Option 2: Run with Uvicorn (recommended for development)
```bash
uvicorn Backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Usage Examples

### 1. Simple Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tell me a joke",
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 2. Conversation with History
```bash
curl -X POST "http://localhost:8000/chat/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my favorite color?",
    "history": [
      {"role": "user", "content": "My favorite color is blue"},
      {"role": "model", "content": "That'\''s nice! Blue is a great color."}
    ],
    "model": "gemini-2.5-flash"
  }'
```

### 3. List Available Models
```bash
curl "http://localhost:8000/models"
```

### 4. Health Check
```bash
curl "http://localhost:8000/health"
```

## 🏗️ Architecture

### AI Module (`AI/`)
The AI module encapsulates all Gemini API interactions:

- **GeminiClient**: Main class for interacting with Gemini AI
  - `generate_content()`: Single-turn content generation
  - `chat_with_history()`: Multi-turn conversations
  - `list_available_models()`: Get available models
  - `generate_stream()`: Streaming responses

### Backend Module (`Backend/`)
The Backend module provides the FastAPI REST API:

- **main.py**: FastAPI application with endpoints
- Pydantic models for request/response validation
- Error handling and logging
- CORS middleware for frontend integration

## 🔑 Available Models

The application supports all current Gemini models:
- `gemini-2.5-flash` (default) - Fast and efficient
- `gemini-2.5-pro` - More capable, slower
- `gemini-2.0-flash` - Alternative fast model
- And many more (check `/models` endpoint)

## 🧪 Testing

Test the API using:
1. **Swagger UI**: Visit http://localhost:8000/docs
2. **curl**: Use the examples above
3. **Python requests**:
   ```python
   import requests
   
   response = requests.post(
       "http://localhost:8000/chat",
       json={"prompt": "Hello, AI!"}
   )
   print(response.json())
   ```

## 🌿 Git Workflow

**IMPORTANT**: Follow this workflow to avoid conflicts:

1. **Always pull latest main first**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create your personal branch**:
   ```bash
   git checkout -b yourname/feature-description
   ```

3. **Make your changes and commit**:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

4. **Push to YOUR branch (NOT main)**:
   ```bash
   git push origin yourname/feature-description
   ```

5. **Create a Pull Request** on GitHub to merge into main

⚠️ **DO NOT push directly to main branch!**

## 🛠️ Development

### Adding New Endpoints

1. Add new methods to `GeminiClient` in `AI/gemini_client.py` if needed
2. Create corresponding FastAPI endpoint in `Backend/main.py`
3. Add Pydantic models for request/response validation
4. Update this README with usage examples

### Environment Variables

Configure the application using `.env` file:

```env
# Required
GEMINI_API_KEY=your_api_key

# Optional (with defaults)
DEFAULT_MODEL=gemini-2.5-flash
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1000
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

## 📝 Notes

- The `google.generativeai` package is deprecated. Consider migrating to `google.genai` in future updates.
- Model names have changed from `gemini-pro` to `gemini-2.5-flash` and similar naming.
- The `/chat/stream` endpoint currently collects all chunks before responding. True SSE streaming can be implemented in future versions.

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure `.env` file exists in the project root
- Check that `GEMINI_API_KEY` is set correctly in `.env`

### "404 models/gemini-xxx is not found"
- Update to current model names (e.g., `gemini-2.5-flash`)
- Check `/models` endpoint for available models

### "500 Internal Server Error"
- Check server console for detailed error messages
- Verify API key is valid
- Ensure all dependencies are installed

## 👥 Contributors

- Your Name (@yourname)

## 📄 License

[Add your license here]
