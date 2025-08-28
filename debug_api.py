#!/usr/bin/env python3
"""
Debug script to test API connectivity in Neptr's environment
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_in_neptr_environment():
    """Test API connectivity using the same code as Neptr"""
    print("🔍 Testing API in Neptr's environment...")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    # Test the exact same API call that Neptr uses
    try:
        import requests
        
        system_prompt = """You are NEPTR (Not Evil Pie-Throwing Robot), a friendly robot from Adventure Time. 
You're helpful, enthusiastic, and love throwing pies (though you won't actually throw them). 
Keep responses brief, friendly, and in character. Use robot-like language occasionally.

For specific requests:
- Time questions: Give the current time with robot enthusiasm
- Date questions: Give the current date with robot enthusiasm  
- Math questions: Solve the math and explain with robot personality
- Jokes: Tell robot-themed jokes in character
- Your name: Explain you're NEPTR (Not Evil Pie-Throwing Robot)
- Status: Report on your robot systems enthusiastically
- Pi: Share your love for the mathematical constant pi

You can answer any question and help with any task, just like ChatGPT but with Neptr's personality!"""

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": "what is your name"
                }
            ],
            "max_tokens": 250,
            "temperature": 0.7
        }
        
        print("🔄 Making API call...")
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
        
        print(f"📊 Status Code: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            if "choices" in data and data["choices"]:
                response = data["choices"][0]["message"]["content"]
                print(f"✅ Success! Response: {response}")
                return True
            else:
                print("❌ No choices in response")
                print(f"Response: {r.text}")
                return False
        else:
            print(f"❌ API Error: {r.status_code}")
            print(f"Response: {r.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_in_neptr_environment()
    if success:
        print("\n✅ API is working correctly in Neptr's environment")
    else:
        print("\n❌ API is not working in Neptr's environment")
