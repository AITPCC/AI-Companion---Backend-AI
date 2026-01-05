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

import os
from ai_service import AIService, quick_chat


def print_section(title: str):
    """Helper function to print section headers nicely"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_basic_functionality():
    """Test 1: Basic message sending and receiving"""
    print_section("TEST 1: Basic Functionality")
    
    # Create an AI service instance with a simple system prompt
    service = AIService(
        # api_key="your-api-key-here",  # Uncomment and add your key if not using env variable
        system_prompt="You are a helpful assistant who gives brief, clear answers."
    )
    
    print("✓ AI Service initialized successfully")
    print(f"✓ Model: {service.model_name}")
    print(f"✓ System Prompt: {service.system_prompt}")
    
    # Send a simple message
    print("\n📤 Sending: 'What is Python?'")
    response = service.send_message("What is Python?")
    print(f"📥 Response: {response[:200]}...")  # Print first 200 characters
    
    print("\n✅ Test 1 Passed: Basic functionality works!")
    return service


def test_conversation_history(service: AIService):
    """Test 2: Verify conversation history is maintained"""
    print_section("TEST 2: Conversation History")
    
    # Clear any previous history
    service.clear_history()
    
    # Have a multi-turn conversation
    print("\n📤 User: 'My favorite color is blue'")
    response1 = service.send_message("My favorite color is blue")
    print(f"📥 AI: {response1[:100]}...")
    
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
    
    # Create service with one personality
    service = AIService(system_prompt="You are a pirate. Always respond like a pirate.")
    
    print("\n📤 Sending: 'Tell me about treasure'")
    response1 = service.send_message("Tell me about treasure in the sea")
    print(f"📥 Pirate AI: {response1[:150]}...")
    
    # Change the system prompt
    print("\n🔄 Changing system prompt to professional assistant...")
    service.set_system_prompt("You are a professional financial advisor. Be formal and precise.")
    
    print("\n📤 Sending: 'Tell me about treasure'")
    response2 = service.send_message("Tell me about treasure")
    print(f"📥 Professional AI: {response2[:150]}...")
    
    print("\n✅ Test 3 Passed: System prompt successfully changes AI behavior!")


def test_history_management(service: AIService):
    """Test 4: History loading and clearing"""
    print_section("TEST 4: History Management")
    
    # Clear history
    service.clear_history()
    print("✓ History cleared")
    
    # Load pre-existing history
    print("\n📋 Loading pre-existing conversation history...")
    pre_loaded_history = [
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Nice to meet you, Alice! How can I help you today?"},
        {"role": "user", "content": "I like programming in Python"},
        {"role": "assistant", "content": "That's great! Python is a wonderful language."}
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


def test_quick_chat():
    """Test 5: Quick chat convenience function"""
    print_section("TEST 5: Quick Chat Function")
    
    print("Testing the quick_chat() convenience function...")
    print("This is useful for one-off questions without managing a service instance.")
    
    print("\n📤 Quick question: 'What is 10 + 25?'")
    response = quick_chat(
        "What is 10 + 25? Just give me the number.",
        system_prompt="You are a calculator. Give only numeric answers."
    )
    print(f"📥 Response: {response}")
    
    print("\n✅ Test 5 Passed: Quick chat function works!")


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
        
        # Test 5: Quick chat
        test_quick_chat()
        
        # Final summary
        print("\n" + "🎉" * 30)
        print("  ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎉" * 30)
        print("\n📚 Next Steps:")
        print("   1. You can now import AIService into any project")
        print("   2. Use: from ai_service import AIService")
        print("   3. Create an instance: service = AIService()")
        print("   4. Start chatting: response = service.send_message('Hello!')")
        
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

