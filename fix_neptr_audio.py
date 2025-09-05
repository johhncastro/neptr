#!/usr/bin/env python3
"""
Fix NEPTR audio to work with Jabra Speak 410
"""

import subprocess
import os
import sys

def test_audio_devices():
    """Test different audio devices to find the working one"""
    print("🔊 Testing Audio Devices for NEPTR")
    print("=" * 40)
    
    # Test 1: Default device
    print("🧪 Test 1: Default audio device")
    try:
        result = subprocess.run([
            "espeak-ng", "-s", "150", "-p", "50", "-v", "en-us", "-g", "10",
            "Testing default audio device"
        ], capture_output=True, text=True, timeout=5)
        print(f"✅ Default device test completed (return code: {result.returncode})")
        if result.stderr:
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Default device test failed: {e}")
    
    # Test 2: Explicit ALSA device
    print("\n🧪 Test 2: ALSA device (card 1)")
    try:
        result = subprocess.run([
            "espeak-ng", "-s", "150", "-p", "50", "-v", "en-us", "-g", "10",
            "Testing ALSA card 1"
        ], env={**os.environ, "AUDIODEV": "hw:1,0"}, capture_output=True, text=True, timeout=5)
        print(f"✅ ALSA card 1 test completed (return code: {result.returncode})")
        if result.stderr:
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"❌ ALSA card 1 test failed: {e}")
    
    # Test 3: PulseAudio device
    print("\n🧪 Test 3: PulseAudio device")
    try:
        result = subprocess.run([
            "espeak-ng", "-s", "150", "-p", "50", "-v", "en-us", "-g", "10",
            "Testing PulseAudio device"
        ], env={**os.environ, "PULSE_SINK": "default"}, capture_output=True, text=True, timeout=5)
        print(f"✅ PulseAudio test completed (return code: {result.returncode})")
        if result.stderr:
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"❌ PulseAudio test failed: {e}")

def create_audio_fix():
    """Create a fixed version of the TTS function"""
    print("\n🔧 Creating Audio Fix for NEPTR")
    print("=" * 40)
    
    # Read the current neptr.py
    with open("neptr.py", "r") as f:
        content = f.read()
    
    # Create backup
    with open("neptr.py.backup", "w") as f:
        f.write(content)
    print("✅ Created backup: neptr.py.backup")
    
    # Find and replace the tts_espeak function
    old_function = '''def tts_espeak(text: str, voice_speed: int, voice_pitch: int):
    """Text-to-speech using espeak with robot-like characteristics"""
    if USE_ESPEAK:
        # Slightly robotic voice with pauses
        subprocess.run([
            "espeak-ng", 
            "-s", str(voice_speed), 
            "-p", str(voice_pitch), 
            "-v", "en-us",
            "-g", str(VOICE_GAP),  # Word gap for more robotic speech
            text
        ], check=False)
    else:
        subprocess.run(["say", "-r", str(voice_speed), text], check=False)'''
    
    new_function = '''def tts_espeak(text: str, voice_speed: int, voice_pitch: int):
    """Text-to-speech using espeak with robot-like characteristics"""
    if USE_ESPEAK:
        # Slightly robotic voice with pauses
        # Try multiple audio devices to ensure output works
        devices_to_try = [
            {},  # Default device
            {"AUDIODEV": "hw:1,0"},  # ALSA card 1
            {"PULSE_SINK": "default"},  # PulseAudio default
        ]
        
        success = False
        for device_env in devices_to_try:
            try:
                env = {**os.environ, **device_env}
                result = subprocess.run([
                    "espeak-ng", 
                    "-s", str(voice_speed), 
                    "-p", str(voice_pitch), 
                    "-v", "en-us",
                    "-g", str(VOICE_GAP),  # Word gap for more robotic speech
                    text
                ], env=env, check=False, timeout=10)
                if result.returncode == 0:
                    success = True
                    break
            except Exception as e:
                continue
        
        if not success:
            print_neptr_status("⚠️  Audio output failed - check audio configuration")
    else:
        subprocess.run(["say", "-r", str(voice_speed), text], check=False)'''
    
    # Replace the function
    if old_function in content:
        new_content = content.replace(old_function, new_function)
        
        # Write the fixed version
        with open("neptr.py", "w") as f:
            f.write(new_content)
        
        print("✅ Fixed NEPTR audio function")
        print("✅ Added multiple audio device support")
        print("✅ Added error handling for audio failures")
    else:
        print("❌ Could not find TTS function to replace")
        return False
    
    return True

def test_fixed_neptr():
    """Test the fixed NEPTR audio"""
    print("\n🧪 Testing Fixed NEPTR Audio")
    print("=" * 40)
    
    try:
        # Import the fixed NEPTR
        sys.path.insert(0, ".")
        from neptr import tts
        
        print("Testing NEPTR TTS function...")
        tts("Hello, this is a test of the fixed NEPTR audio output")
        print("✅ NEPTR TTS test completed")
        
    except Exception as e:
        print(f"❌ NEPTR TTS test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🤖 NEPTR Audio Fix for Jabra Speak 410")
    print("=" * 50)
    
    # Test current audio setup
    test_audio_devices()
    
    # Create the fix
    if create_audio_fix():
        # Test the fixed version
        test_fixed_neptr()
        
        print("\n🎉 Audio Fix Complete!")
        print("=" * 30)
        print("✅ NEPTR audio function has been fixed")
        print("✅ Multiple audio devices are now supported")
        print("✅ Error handling has been added")
        print()
        print("🚀 Try running NEPTR now:")
        print("   python3 neptr.py")
        print()
        print("💡 If it still doesn't work:")
        print("   - Check that espeak-ng is working: espeak-ng 'Hello'")
        print("   - Check audio device: aplay -l")
        print("   - Check volume levels: alsamixer")
        print("   - Restore backup if needed: cp neptr.py.backup neptr.py")
    else:
        print("❌ Failed to create audio fix")

if __name__ == "__main__":
    main()
