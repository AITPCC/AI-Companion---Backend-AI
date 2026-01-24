# 🤖 AI Companion Backend

A FastAPI-based backend service that provides an AI companion interface using Google's Gemini AI. This project enables conversational interactions with a customizable AI persona, featuring conversation history management and flexible configuration options.

## 📋 Table of Contents

- [Project Description](#-project-description)
- [Tech Stack](#-tech-stack)
- [Folder Structure](#-folder-structure)
- [Local Setup Guide](#-local-setup-guide)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)

## 🎯 Project Description

AI Companion Backend is a RESTful API service built with FastAPI that integrates with Google's Gemini AI to provide intelligent conversational experiences. The service supports:

- **Customizable AI Personas**: Configure the AI to adopt different historical perspectives and personalities
- **Conversation History**: Maintain context across multiple interactions
- **Flexible Configuration**: Adjust model parameters like temperature, max tokens, and model selection
- **Production-Ready**: Built with FastAPI for high performance and automatic API documentation

The service is designed to be easily extensible, allowing you to plug in different AI models and customize the conversation experience to your needs.

## 🛠 Tech Stack

### Core Framework

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs with Python
- **[Python 3.12+](https://www.python.org/)** - Programming language

### AI & ML

- **[Google Gemini AI](https://ai.google.dev/)** - Google's generative AI model via `google-adk`
- **Custom System Prompts** - Configurable AI personality and behavior

### Development Tools

- **[uv](https://github.com/astral-sh/uv)** - Fast Python package installer and resolver
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation using Python type annotations
- **[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** - Settings management

### Project Management

- **pyproject.toml** - Modern Python project configuration
- **uv.lock** - Dependency lock file for reproducible builds

## 📁 Folder Structure

```
AI-Companion---Backend-AI/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── logger.py                 # Logging configuration
│   │
│   ├── api/                      # API routes and routers
│   │   ├── __init__.py
│   │   ├── router.py             # Main API router that combines all routes
│   │   └── routes/               # Individual route modules
│   │       ├── __init__.py
│   │       ├── chat.py           # Chat endpoint (/chat)
│   │       └── health.py         # Health check endpoint (/health)
│   │
│   ├── core/                     # Core application configuration
│   │   ├── __init__.py
│   │   └── config.py             # Settings and environment configuration
│   │
│   ├── schema/                   # Pydantic models and schemas
│   │   ├── __init__.py
│   │   └── schemas.py            # Request/Response models (ChatRequest, ChatResponse, etc.)
│   │
│   ├── services/                 # Business logic and services
│   │   ├── __init__.py
│   │   ├── ai_service.py         # AI service implementation (Gemini integration)
│   │   ├── test.py               # Service tests
│   │   └── AI_SERVICE_README.md  # AI service documentation
│   │
│   ├── ai/                       # AI-related configurations
│   │   ├── __init__.py
│   │   └── prompts/              # System prompts and AI personality definitions
│   │       ├── __init__.py
│   │       └── chat_system_prompt.py  # System prompt for chat persona
│   │
│   └── .env.sample               # Environment variables template
│
├── pyproject.toml               # Project dependencies and metadata
├── uv.lock                      # Locked dependency versions
├── .python-version              # Python version specification
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

### Key Directories Explained

- **`app/api/`**: Contains all API route definitions. Routes are organized by feature (chat, health) and combined in `router.py`.
- **`app/core/`**: Core application settings loaded from environment variables.
- **`app/schema/`**: Pydantic models that define request/response structures and validation rules.
- **`app/services/`**: Business logic layer, including the AI service that handles Gemini API interactions.
- **`app/ai/prompts/`**: System prompts that define the AI's personality and behavior patterns.

## 🚀 Local Setup Guide

This guide will help you set up the project locally using `uv`, a fast Python package installer.

### Prerequisites

- **Python 3.12 or higher** installed on your system
- **uv** installed (see installation instructions below)
- **Google Gemini API Key** (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Step 1: Install uv

If you don't have `uv` installed, install it using one of these methods:

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/AITPCC/AI-Companion---Backend-AI.git
cd AI-Companion---Backend-AI
```

### Step 3: Set Up Environment Variables

1. Copy the environment sample file:

   ```bash
   cp app/.env.sample app/.env
   ```

2. Edit `app/.env` and add your Google Gemini API key:

   ```env
   GOOGLE_API_KEY=your-actual-api-key-here
   ```

### Step 4: Install Dependencies

Use `uv` to sync dependencies (this will create a virtual environment automatically):

```bash
uv sync
```

This command will:

- Create a virtual environment (`.venv/`)
- Install all dependencies from `pyproject.toml`
- Generate/update `uv.lock` file

### Step 5: Run the Application

**Option 1: Using uv run (Recommended)**

```bash
uv run fastapi dev app/main.py
```

**Option 2: Activate virtual environment first**

```bash
# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Run the application
fastapi dev app/main.py
```

The server will start at `http://127.0.0.1:8000`

### Step 6: Verify Installation

1. **Check health endpoint:**

   ```bash
   curl http://127.0.0.1:8000/health
   ```

   Expected response: `{"status":"ok"}`

2. **View API documentation:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

### Troubleshooting

**Issue: `uv: command not found`**

- Make sure `uv` is installed and in your PATH
- Try restarting your terminal

**Issue: `SEGV` (Segmentation Fault)**

- Ensure you're using Python 3.12 or higher
- Check that `.python-version` contains a valid Python version (e.g., `3.12`)
- Try removing `.venv` and running `uv sync` again

**Issue: `GOOGLE_API_KEY not found`**

- Verify that `app/.env` exists and contains `GOOGLE_API_KEY`
- Check that the API key is valid and has proper permissions

**Issue: Import errors**

- Make sure you're running commands from the project root directory
- Verify that `uv sync` completed successfully

## 📡 API Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the service.

**Response:**

```json
{
  "status": "ok"
}
```

### Chat

```http
POST /chat
```

Send a message to the AI companion and receive a response.

**Request Body:**

```json
{
  "message": "Hello, how are you?",
  "history": [],
  "config": {
    "mode": "history_figure"
  }
}
```

**Response:**

```json
{
  "status": 200,
  "content": "I am well, thank you for asking...",
  "error": null
}
```

## ⚙️ Configuration

Configuration is managed through environment variables in `app/.env`:

| Variable            | Description                 | Default            |
| ------------------- | --------------------------- | ------------------ |
| `GOOGLE_API_KEY`    | Your Google Gemini API key  | **Required**       |
| `MODEL_NAME`        | Gemini model to use         | `gemini-2.5-flash` |
| `TEMPERATURE`       | Model temperature (0.0-1.0) | `0.7`              |
| `MAX_OUTPUT_TOKENS` | Maximum tokens in response  | `1000`             |

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Pydantic Documentation](https://docs.pydantic.dev/)

**Happy Coding! 🚀**
