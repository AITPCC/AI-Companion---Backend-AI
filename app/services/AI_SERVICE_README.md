# AITPCC-AI Service

A clean, reusable AI service built with Google's Gemini API that you can easily plug into any project.

### Task 1: Code Encapsulation ✓
- **Created `ai_service.py`**: A well-structured class-based service
- **Created `test.py`**: Comprehensive tests to verify functionality
- **Ready to plug into other projects**: Just import and use!

### Task 2: Prompt Engineering ✓
- **System Prompt Support**: Define AI personality/behavior
- **History Management**: Function accepts and maintains conversation history
- **Full History Control**: Load, save, and clear conversation history


## Quick Start

### Step 1: Get Your API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### Step 2: Set Up Your API Key

**Option A: Environment Variable (Recommended)**

```bash
# In your terminal:
export GOOGLE_API_KEY="your-api-key-here"
```

**Option B: Direct in Code**

```python
service = AIService(api_key="your-api-key-here")
```

### Step 3: Run the Tests

```bash
# Make sure you're in the project directory
cd /Users/mayouran/Desktop/AITPCC-AI

# Activate virtual environment
source venv/bin/activate

# Run tests
python test.py
```

## 📚 How to Use AIService

### Basic Example

```python
from ai_service import AIService

# Create service instance
service = AIService(
    system_prompt="You are a helpful coding assistant."
)

# Send a message
response = service.send_message("What is Python?")
print(response)
```

### Example with Conversation History

```python
from ai_service import AIService

service = AIService()

# First message
service.send_message("My name is Alice")

# Second message - AI remembers the first one!
response = service.send_message("What's my name?")
print(response)  # Will mention "Alice"

# Get full history
history = service.get_history()
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### Example: Changing System Prompt

```python
from ai_service import AIService

# Start with one personality
service = AIService(
    system_prompt="You are a pirate. Always talk like a pirate."
)

response = service.send_message("Hello!")
# Response will be in pirate speak!

# Change personality
service.set_system_prompt("You are a professional teacher.")
response = service.send_message("Hello!")
# Now response will be professional
```

### Example: Loading Pre-existing History

```python
from ai_service import AIService

service = AIService()

# Load previous conversation
old_conversation = [
    {"role": "user", "content": "I love Python"},
    {"role": "assistant", "content": "Python is great!"}
]
service.load_history(old_conversation)

# AI now remembers this conversation
response = service.send_message("What do I love?")
print(response)  # Will mention Python
```

### Example: Quick One-off Questions

```python
from ai_service import quick_chat

# For simple questions without needing to manage history
response = quick_chat("What is 2 + 2?")
print(response)
```

## 🔧 Key Features Explained

### 1. System Prompt (Task 2 Requirement ✓)

The **system prompt** is like giving the AI instructions on how to behave. It's the first thing the AI reads before any conversation.

```python
# Make AI act as a coding tutor
service = AIService(
    system_prompt="You are a patient coding tutor. Explain concepts simply."
)
```

**Why it's useful:**
- Controls AI personality
- Sets response style (formal, casual, technical, etc.)
- Defines AI's role (teacher, assistant, expert, etc.)

### 2. Conversation History (Task 2 Requirement ✓)

The **history** is a list of all messages exchanged between user and AI.

```python
# History format:
[
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "I don't have access to weather data."}
]
```

**Why it's useful:**
- AI remembers context from earlier in conversation
- You can save/load conversations
- You can analyze what was discussed

### 3. Encapsulation (Task 1 Requirement ✓)

All AI functionality is wrapped in the `AIService` class. This means:

**Before (messy prototype):**
```python
# Code scattered everywhere
api_key = "..."
model = genai.GenerativeModel(...)
history = []
# More scattered code...
```

**After (clean encapsulation):**
```python
# Everything in one place
service = AIService()
response = service.send_message("Hello")
```

**Benefits:**
- Easy to understand
- Easy to reuse
- Easy to maintain
- Can plug into any project

## 🔌 Plugging into Other Projects

To use this in another project:

```bash
# 1. Copy ai_service.py to your project
cp ai_service.py /path/to/your/project/

# 2. In your project code:
from ai_service import AIService

service = AIService()
response = service.send_message("Your message here")
```

Or use it as a git submodule:

```bash
cd your-project
git submodule add <your-repo-url> ai_service
```

## 🧪 Understanding test.py

The test file does 5 things:

1. **Test 1**: Verifies basic send/receive works
2. **Test 2**: Checks that AI remembers conversation history
3. **Test 3**: Tests changing system prompt changes behavior
4. **Test 4**: Verifies history loading/clearing works
5. **Test 5**: Tests the quick_chat convenience function

## 📖 For Beginners: Key Concepts

### What is a Class?

A **class** is like a blueprint for creating objects. Think of it like a cookie cutter:

```python
# AIService is the class (cookie cutter)
service = AIService()  # service is an object (cookie)

# You can make multiple objects from one class
service1 = AIService(system_prompt="Be helpful")
service2 = AIService(system_prompt="Be funny")
```

### What is a Method?

A **method** is a function that belongs to a class:

```python
service = AIService()
response = service.send_message("Hello")  # send_message is a method
#                    ^^^^^^^^^^^^
#                    This is a method call
```

### What is `self`?

`self` refers to the specific object (instance) of the class:

```python
class AIService:
    def __init__(self):
        self.history = []  # This object's history
    
    def send_message(self, message):
        self.history.append(...)  # Add to THIS object's history
```

### What is `__init__`?

`__init__` is a special method that runs automatically when you create a new object:

```python
service = AIService()  # __init__ runs here automatically!
```

## 🎯 Common Use Cases

### Use Case 1: Chatbot for Your Website

```python
from ai_service import AIService

# Create a customer service chatbot
chatbot = AIService(
    system_prompt="You are a friendly customer service agent for TechStore."
)

# Handle user messages
user_message = "Do you have refunds?"
response = chatbot.send_message(user_message)
```

### Use Case 2: Code Review Assistant

```python
from ai_service import AIService

reviewer = AIService(
    system_prompt="You are a code reviewer. Find bugs and suggest improvements."
)

code = """
def add(a, b):
    return a + b
"""

response = reviewer.send_message(f"Review this code:\n{code}")
```

### Use Case 3: Learning Buddy

```python
from ai_service import AIService

tutor = AIService(
    system_prompt="You are a patient tutor. Explain concepts step-by-step."
)

response = tutor.send_message("Explain what a loop is in programming")
```

## Troubleshooting

### Error: "No API key provided"

**Solution:** Set your API key:
```bash
export GOOGLE_API_KEY="your-key-here"
```

### Error: "Module not found"

**Solution:** Activate your virtual environment:
```bash
source venv/bin/activate
```

### Error: "Rate limit exceeded"

**Solution:** Google has free tier limits. Wait a moment or upgrade your plan.

## 📝 Next Steps

1. ✅ Run `python test.py` to verify everything works
2. ✅ Try modifying the system prompts in test.py
3. ✅ Create your own script that uses AIService
4. ✅ Plug ai_service.py into your own projects!

## 🤝 Contributing

Feel free to extend this service with:
- Support for other AI models
- Streaming responses
- Token counting
- Cost tracking
- Multi-modal support (images, audio)



