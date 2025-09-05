#!/usr/bin/env python3
"""
Test espeak TTS for NEPTR
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neptr import tts, print_neptr_status

def test_espeak_tts():
    """Test espeak TTS engine"""
    print("🎤 Testing espeak TTS for Neptr's Voice")
    print("=" * 50)
    
    test_text = "Beep boop! I am NEPTR, Not Evil Pie-Throwing Robot! Finn's best robot friend!"
    
    print(f"\n🔊 Testing espeak: Basic robotic voice")
    print("-" * 40)
    
    try:
        print(f"Playing: '{test_text}'")
        tts(test_text)
        print("✅ espeak TTS test completed!")
        
    except Exception as e:
        print(f"❌ Error with espeak: {e}")

def test_voice_settings():
    """Test different voice settings"""
    print("\n🎵 Testing Different Voice Settings")
    print("=" * 40)
    
    test_text = "Beep boop! I am NEPTR, your friendly pie-throwing robot!"
    
    # Test different speeds
    speeds = [150, 175, 200]
    for speed in speeds:
        print(f"\n🔊 Testing speed: {speed}")
        print("-" * 20)
        try:
            tts(test_text, voice_speed=speed)
            input("Press Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test different pitches
    pitches = [25, 35, 50]
    for pitch in pitches:
        print(f"\n🔊 Testing pitch: {pitch}")
        print("-" * 20)
        try:
            tts(test_text, voice_pitch=pitch)
            input("Press Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🤖 NEPTR Voice Testing")
    print("=" * 30)
    
    choice = input("Test (1) espeak TTS, (2) voice settings, or (3) both? [1]: ").strip()
    
    if choice == "2":
        test_voice_settings()
    elif choice == "3":
        test_espeak_tts()
        test_voice_settings()
    else:
        test_espeak_tts()