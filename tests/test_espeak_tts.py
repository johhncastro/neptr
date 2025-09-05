#!/usr/bin/env python3
"""
Simple test for espeak TTS
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neptr import tts, print_neptr_status

def test_espeak_tts():
    """Test espeak TTS for Neptr's voice"""
    print("🎤 Testing espeak TTS for Neptr's Voice")
    print("=" * 40)
    
    test_text = "Beep boop! I am NEPTR, Not Evil Pie-Throwing Robot!"
    
    # Test the current configuration
    print(f"🔊 Testing current config: {test_text}")
    tts(test_text)
    
    print("\n✅ espeak TTS test completed!")
    print("🎯 To change voice settings, edit config.py:")
    print("   VOICE_SPEED = 175  # Speech speed")
    print("   VOICE_PITCH = 35   # Voice pitch")

if __name__ == "__main__":
    test_espeak_tts()
