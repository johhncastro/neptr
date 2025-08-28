#!/usr/bin/env python3
"""
Demo script for NEPTR AI Assistant
This allows you to test Neptr's responses without voice input
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neptr import handle_intent, tts, print_neptr_status

def demo_conversation():
    """Demo conversation with Neptr"""
    print("🤖 NEPTR AI Assistant - Demo Mode")
    print("=" * 40)
    print("This demo shows Neptr's responses to various commands.")
    print("Enhanced with GPT-4 Turbo for current information!")
    print("Personality matches Neptr from Adventure Time!")
    print("You can also test voice output by setting AUDIO_DEMO = True below.")
    print()
    
    # Set to True to hear Neptr speak
    AUDIO_DEMO = False
    
    # Demo commands
    demo_commands = [
        "what time is it",
        "what's the date today", 
        "what's your name",
        "tell me a joke",
        "calculate 15 plus 27",
        "tell me about pi",
        "how are you feeling",
        "what can you do",
        "who created you",
        "do you like pie",
        "what is the capital of France",
        "how do I make a cake",
        "explain quantum physics",
        "tell me a story about a robot",
        "who is the current president of the united states",
        "tell me about your adventures with Finn",
        "what's happening in the news today"
    ]
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n{i}. You: {command}")
        response = handle_intent(command)
        print(f"   Neptr: {response}")
        
        if AUDIO_DEMO:
            tts(response)
            input("   Press Enter to continue...")
    
    print("\n" + "=" * 40)
    print("🎉 Demo complete! Neptr is working perfectly!")
    print("\nTo run the full voice assistant:")
    print("   python3 neptr.py")

def interactive_demo():
    """Interactive demo where you can type commands"""
    print("🤖 NEPTR AI Assistant - Interactive Demo")
    print("=" * 40)
    print("Type commands to chat with Neptr!")
    print("Type 'quit' or 'exit' to end the demo.")
    print("Type 'audio on' or 'audio off' to toggle voice output.")
    print()
    
    audio_enabled = False
    
    while True:
        try:
            command = input("You: ").strip()
            
            if command.lower() in ['quit', 'exit', 'bye']:
                print("Neptr: Goodbye! It was great chatting with you!")
                break
            elif command.lower() == 'audio on':
                audio_enabled = True
                print("Neptr: Voice output enabled!")
                continue
            elif command.lower() == 'audio off':
                audio_enabled = False
                print("Neptr: Voice output disabled!")
                continue
            elif not command:
                continue
            
            response = handle_intent(command)
            print(f"Neptr: {response}")
            
            if audio_enabled:
                tts(response)
                
        except KeyboardInterrupt:
            print("\nNeptr: Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        demo_conversation()
