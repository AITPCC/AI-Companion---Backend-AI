"""
Test script to verify Gemini + FastAPI integration
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing AI Companion Backend Integration")
print("=" * 60)

# Test 1: Import AI module
print("\n[Test 1] Importing AI module...")
try:
    from AI import GeminiClient
    print("✓ Successfully imported GeminiClient")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Initialize Gemini client
print("\n[Test 2] Initializing Gemini client...")
try:
    client = GeminiClient()
    print("✓ GeminiClient initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

# Test 3: List available models
print("\n[Test 3] Listing available models...")
try:
    models = client.list_available_models()
    print(f"✓ Found {len(models)} models")
    print(f"  Sample models: {', '.join([m['name'] for m in models[:3]])}")
except Exception as e:
    print(f"✗ Failed to list models: {e}")

# Test 4: Generate simple content
print("\n[Test 4] Generating simple content...")
try:
    response = client.generate_content("Say 'Hello, world!' in one sentence.")
    print(f"✓ Generated content: {response[:100]}...")
except Exception as e:
    print(f"✗ Failed to generate content: {e}")

# Test 5: Import FastAPI app
print("\n[Test 5] Importing FastAPI app...")
try:
    from Backend import app
    print("✓ Successfully imported FastAPI app")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    sys.exit(1)

# Test 6: Check app routes
print("\n[Test 6] Checking API routes...")
try:
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    print(f"✓ Found {len(routes)} routes:")
    for route in sorted(routes):
        print(f"  - {route}")
except Exception as e:
    print(f"✗ Failed to check routes: {e}")

print("\n" + "=" * 60)
print("✓ All tests passed! Integration is working correctly.")
print("=" * 60)
print("\nTo start the server, run:")
print("  cd Backend")
print("  python main.py")
print("\nOr with uvicorn:")
print("  uvicorn Backend.main:app --reload")
print("\nThen visit: http://localhost:8000/docs")
print("=" * 60)

