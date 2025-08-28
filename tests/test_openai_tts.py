#!/usr/bin/env python3
"""
Simple test for OpenAI TTS
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neptr import tts, print_neptr_status

def test_openai_tts():
    """Test OpenAI TTS with different voices"""
    print("🎤 Testing OpenAI TTS for Neptr's Voice")
    print("=" * 40)
    
    test_text = "Beep boop! I am NEPTR, Not Evil Pie-Throwing Robot!"
    
    # Test the current configuration
    print(f"🔊 Testing current config: {test_text}")
    tts(test_text)
    
    print("\n✅ OpenAI TTS test completed!")
    print("🎯 To change voices, edit config.py:")
    print("   OPENAI_TTS_VOICE = 'alloy'  # Try: alloy, echo, onyx, fable, nova, shimmer")

if __name__ == "__main__":
    test_openai_tts()
