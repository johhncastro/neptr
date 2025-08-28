#!/usr/bin/env python3
"""
Test script to try different TTS engines for Neptr's voice
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neptr import tts, print_neptr_status

def test_tts_engines():
    """Test different TTS engines"""
    print("🎤 Testing TTS Engines for Neptr's Voice")
    print("=" * 50)
    
    test_text = "Beep boop! I am NEPTR, Not Evil Pie-Throwing Robot! Finn's best robot friend!"
    
    engines = [
        ("espeak", "Basic robotic voice"),
        ("openai", "OpenAI TTS (if API key available)"),
        ("piper", "Piper TTS (if installed)")
    ]
    
    for engine_name, description in engines:
        print(f"\n🔊 Testing {engine_name}: {description}")
        print("-" * 40)
        
        try:
            # Temporarily set the TTS engine
            import config
            original_engine = config.TTS_ENGINE
            config.TTS_ENGINE = engine_name
            
            print(f"Playing: '{test_text}'")
            tts(test_text)
            
            # Restore original engine
            config.TTS_ENGINE = original_engine
            
            input("Press Enter to continue to next engine...")
            
        except Exception as e:
            print(f"❌ Error with {engine_name}: {e}")
            input("Press Enter to continue...")

def test_openai_voices():
    """Test different OpenAI TTS voices"""
    print("\n🎵 Testing OpenAI TTS Voices")
    print("=" * 30)
    
    voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    test_text = "Beep boop! I am NEPTR, your friendly pie-throwing robot!"
    
    for voice in voices:
        print(f"\n🔊 Testing OpenAI voice: {voice}")
        print("-" * 30)
        
        try:
            import requests
            import tempfile
            import subprocess
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OpenAI API key not set")
                break
                
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "tts-1",
                "input": test_text,
                "voice": voice
            }
            
            response = requests.post(
                "https://api.openai.com/v1/audio/speech",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    f.write(response.content)
                    temp_file = f.name
                
                print(f"Playing: '{test_text}'")
                subprocess.run(["afplay", temp_file], check=False)
                os.unlink(temp_file)
                
                input("Press Enter to continue...")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🤖 Neptr Voice Testing Tool")
    print("=" * 30)
    print("This tool helps you find the best TTS engine for Neptr's voice")
    print()
    
    while True:
        print("Choose an option:")
        print("1. Test all TTS engines")
        print("2. Test OpenAI voices only")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            test_tts_engines()
        elif choice == "2":
            test_openai_voices()
        elif choice == "3":
            print("Goodbye! 🤖🥧")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
