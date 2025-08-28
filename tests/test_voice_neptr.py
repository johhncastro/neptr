#!/usr/bin/env python3
"""
Test script to debug Neptr voice assistant issues
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neptr import handle_intent, print_neptr_status

def test_voice_simulation():
    """Simulate voice commands to test Neptr's responses"""
    print("🤖 Testing Neptr Voice Assistant Simulation")
    print("=" * 50)
    print("This simulates what happens when you speak to Neptr")
    print()
    
    # Test commands that you might say
    test_commands = [
        "what time is it",
        "tell me a joke", 
        "what's your name",
        "how are you feeling",
        "what is the capital of France"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"🎤 Simulated voice command {i}: '{command}'")
        print_neptr_status(f"Processing: '{command}'")
        
        try:
            response = handle_intent(command)
            print(f"🤖 Neptr response: {response}")
        except Exception as e:
            print(f"❌ Error processing command: {e}")
        
        print("-" * 40)
        print()

def test_api_connection():
    """Test OpenAI API connection specifically"""
    print("🔌 Testing OpenAI API Connection")
    print("=" * 30)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    try:
        import requests
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello Neptr"}],
            "max_tokens": 50
        }
        
        print("🔄 Testing API call...")
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            if "choices" in data and data["choices"]:
                response = data["choices"][0]["message"]["content"]
                print(f"✅ API working! Response: {response}")
                return True
            else:
                print("❌ API returned no choices")
                return False
        else:
            print(f"❌ API error: {r.status_code} - {r.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    print("🔍 Neptr Voice Assistant Debug Test")
    print("=" * 50)
    
    # Test 1: API Connection
    print("1. Testing OpenAI API connection...")
    api_working = test_api_connection()
    print()
    
    # Test 2: Voice Simulation
    print("2. Testing voice command processing...")
    test_voice_simulation()
    
    print("=" * 50)
    if api_working:
        print("✅ API is working - issue might be with voice processing")
        print("💡 Try running: python3 neptr.py")
    else:
        print("❌ API connection issue detected")
        print("💡 Check your API key and internet connection")

if __name__ == "__main__":
    main()
