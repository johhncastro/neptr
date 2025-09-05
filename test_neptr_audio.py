#!/usr/bin/env python3
"""
Simple test script for NEPTR audio
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_neptr_audio():
    """Test NEPTR audio output"""
    print("🤖 NEPTR Audio Test")
    print("=" * 20)
    
    try:
        from neptr import tts
        print("✅ NEPTR TTS function imported successfully")
        
        print("🧪 Testing TTS output...")
        tts("Hello, this is a test of NEPTR's voice output")
        print("✅ TTS test completed")
        
        print("🧪 Testing with different message...")
        tts("Beep boop! I am NEPTR, the Never Ending Pie Throwing Robot!")
        print("✅ Second TTS test completed")
        
        print("\n🎉 NEPTR audio test successful!")
        print("If you heard the audio, NEPTR is working correctly!")
        
    except Exception as e:
        print(f"❌ NEPTR audio test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_neptr_audio()
