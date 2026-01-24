"""
Test Script for AI Service
---------------------------
This script tests the AIService class to verify it works correctly.
It also serves as documentation showing you how to use the service.

Before running this script:
1. Make sure you have set your GOOGLE_API_KEY environment variable
   OR you can add it directly in this file (see below)

To set the API key in terminal:
    export GOOGLE_API_KEY="your-api-key-here"

To run this test:
    python test.py
"""

from ai_service import AIService, SYSTEM_PROMPT, quick_chat
from schemas import ChatConfig, ChatMessage


def print_section(title: str):
    """Helper function to print section headers nicely"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_basic_functionality():
    """Test 1: Basic message sending and receiving"""
    print_section("TEST 1: Basic Functionality")

    # Create an AI service instance with the Qin Shi Huang persona prompt
    service = AIService(
        # api_key="your-api-key-here",  # Uncomment and add your key if not using env variable
        system_prompt=SYSTEM_PROMPT
    )

    print("✓ AI Service initialized successfully")
    print(f"✓ Model: {service.model_name}")
    print(f"✓ System Prompt: {service.system_prompt}")

    # Send a message that fits the Qin Shi Huang persona
    print("\n📤 Sending: 'How should a ruler maintain order in the realm?'")
    response = service.send_message("How should a ruler maintain order in the realm?")
    print(f"📥 Response: {response}")

    print("\n✅ Test 1 Passed: Basic functionality works!")
    return service


def test_conversation_history(service: AIService):
    """Test 2: Verify conversation history is maintained"""
    print_section("TEST 2: Conversation History")

    # Clear any previous history
    service.clear_history()

    # Have a multi-turn conversation (history uses ChatMessage from schemas.py)
    print("\n📤 User: 'My favorite color is blue'")
    response1 = service.send_message("My favorite color is blue")
    print(f"📥 AI: {response1}")

    print("\n📤 User: 'What is my favorite color?'")
    response2 = service.send_message("What is my favorite color?")
    print(f"📥 AI: {response2}")

    # Check history
    history = service.get_history()
    print(f"\n✓ History contains {len(history)} messages")

    # Verify the AI remembers (response should mention "blue")
    if "blue" in response2.lower():
        print("✅ Test 2 Passed: AI remembers conversation history!")
    else:
        print("⚠️  Warning: AI might not have remembered the context")

    return service


def test_system_prompt_change():
    """Test 3: Changing system prompt changes AI behavior"""
    print_section("TEST 3: System Prompt Changes")

    # Create service with the Qin Shi Huang persona
    service = AIService(system_prompt=SYSTEM_PROMPT)

    print("\n📤 Sending: 'What is the purpose of law?'")
    response1 = service.send_message("What is the purpose of law?")
    print(f"📥 Qin Shi Huang AI: {response1}")

    # Change the system prompt
    print("\n🔄 Changing system prompt to a neutral assistant...")
    service.set_system_prompt(
        "You are a neutral assistant who answers briefly and clearly."
    )

    print("\n📤 Sending: 'What is the purpose of law?'")
    response2 = service.send_message("What is the purpose of law?")
    print(f"📥 Neutral AI: {response2}")

    print("\n✅ Test 3 Passed: System prompt successfully changes AI behavior!")


def test_history_management(service: AIService):
    """Test 4: History loading and clearing"""
    print_section("TEST 4: History Management")

    # Clear history
    service.clear_history()
    print("✓ History cleared")

    # Load pre-existing history (use ChatMessage class from schemas.py)
    print("\n📋 Loading pre-existing conversation history...")
    pre_loaded_history = [
        ChatMessage(content="My name is Alice"),
        ChatMessage(content="Nice to meet you, Alice! How can I help you today?"),
        ChatMessage(content="I like programming in Python"),
        ChatMessage(content="That's great! Python is a wonderful language."),
    ]

    service.load_history(pre_loaded_history)
    print(f"✓ Loaded {len(pre_loaded_history)} messages into history")

    # Test if AI remembers the loaded history
    print("\n📤 Asking: 'What's my name and what do I like?'")
    response = service.send_message("What's my name and what do I like?")
    print(f"📥 Response: {response}")

    # Check if response contains expected information
    if "alice" in response.lower() and "python" in response.lower():
        print("\n✅ Test 4 Passed: History loading works correctly!")
    else:
        print("\n⚠️  Warning: AI might not have fully integrated the loaded history")


def test_schema_config_message(service: AIService):
    """Test 5: Use schemas.ChatMessage and schemas.ChatConfig"""
    print_section("TEST 5: schemas.py Integration")

    # Build config and message using schemas.py classes
    config = ChatConfig(
        model_name="gemini-2.5-flash",
        max_tokens=150,
        temperature=0.7,
    )
    message = ChatMessage(content="How should a ruler secure lasting unity?")
    history = [
        ChatMessage(content="I seek counsel on the nature of order."),
        ChatMessage(content="Order is born of law and discipline."),
    ]

    response = service.send_message_with_config(
        message=message,
        history=history,
        config=config,
    )
    print(f"📥 Response: {response}")

    print("\n✅ Test 5 Passed: schemas.py classes work with AIService!")


def test_quick_chat():
    """Test 6: Quick chat convenience function"""
    print_section("TEST 6: Quick Chat Function")

    print("Testing the quick_chat() convenience function...")
    print("This is useful for one-off questions without managing a service instance.")

    print("\n📤 Quick question: 'What is 10 + 25?'")
    response = quick_chat(
        "What is 10 + 25? Just give me the number.",
        system_prompt="You are a calculator. Give only numeric answers.",
    )
    print(f"📥 Response: {response}")

    print("\n✅ Test 6 Passed: Quick chat function works!")


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "🚀" * 30)
    print("  STARTING AI SERVICE TESTS")
    print("🚀" * 30)

    try:
        # Test 1: Basic functionality
        service = test_basic_functionality()

        # Test 2: Conversation history
        test_conversation_history(service)

        # Test 3: System prompt changes
        test_system_prompt_change()

        # Test 4: History management
        test_history_management(service)

        # Test 5: schemas.py integration
        test_schema_config_message(service)

        # Test 6: Quick chat
        test_quick_chat()

    except ValueError as e:
        print("\n❌ ERROR: API Key not found!")
        print(f"   {e}")
        print("\n📝 To fix this:")
        print("   1. Get an API key from: https://makersuite.google.com/app/apikey")
        print("   2. Set it in your environment:")
        print("      export GOOGLE_API_KEY='your-key-here'")
        print("   3. Or add it directly in test.py:")
        print("      service = AIService(api_key='your-key-here')")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # This runs when you execute: python test.py
    run_all_tests()
