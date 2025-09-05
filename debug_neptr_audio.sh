#!/bin/bash

# Debug NEPTR Audio Script
# This script will help identify why NEPTR audio isn't working

echo "🤖 NEPTR Audio Debug Script"
echo "=========================="
echo

# Test 1: Direct espeak-ng test
echo "🧪 Test 1: Direct espeak-ng"
echo "Running: espeak-ng 'Hello from NEPTR'"
timeout 5 espeak-ng "Hello from NEPTR" 2>&1
echo "✅ Direct espeak-ng test completed"
echo

# Test 2: espeak-ng with same parameters as NEPTR
echo "🧪 Test 2: espeak-ng with NEPTR parameters"
echo "Running: espeak-ng -s 150 -p 50 -v en-us -g 10 'Hello from NEPTR'"
timeout 5 espeak-ng -s 150 -p 50 -v en-us -g 10 "Hello from NEPTR" 2>&1
echo "✅ NEPTR parameter test completed"
echo

# Test 3: Check NEPTR TTS function
echo "🧪 Test 3: NEPTR TTS Function Test"
cat > test_neptr_tts.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from neptr import tts
    print("Testing NEPTR TTS function...")
    tts("Hello, this is a test of NEPTR's voice output")
    print("NEPTR TTS test completed")
except Exception as e:
    print(f"NEPTR TTS test failed: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 test_neptr_tts.py
rm -f test_neptr_tts.py
echo

# Test 4: Check NEPTR configuration
echo "🧪 Test 4: NEPTR Configuration Check"
cat > check_neptr_config.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import config
    print(f"AUDIO_FEEDBACK: {config.AUDIO_FEEDBACK}")
    print(f"USE_ESPEAK: {config.USE_ESPEAK}")
    print(f"VOICE_SPEED: {config.VOICE_SPEED}")
    print(f"VOICE_PITCH: {config.VOICE_PITCH}")
    print(f"VOICE_GAP: {config.VOICE_GAP}")
except Exception as e:
    print(f"Config check failed: {e}")
EOF

python3 check_neptr_config.py
rm -f check_neptr_config.py
echo

# Test 5: Check audio device in use
echo "🧪 Test 5: Audio Device Check"
echo "Current default audio device:"
aplay -D default /dev/zero 2>&1 | head -3 &
sleep 1
kill $! 2>/dev/null
echo

# Test 6: Check if NEPTR is using the right audio device
echo "🧪 Test 6: NEPTR Audio Device Test"
cat > test_neptr_device.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from neptr import tts_espeak
    
    print("Testing NEPTR espeak function directly...")
    # Test with explicit audio device
    result = subprocess.run([
        "espeak-ng", 
        "-s", "150", 
        "-p", "50", 
        "-v", "en-us",
        "-g", "10",
        "Hello from NEPTR espeak test"
    ], capture_output=True, text=True)
    
    print(f"Return code: {result.returncode}")
    if result.stderr:
        print(f"Error output: {result.stderr}")
    if result.stdout:
        print(f"Standard output: {result.stdout}")
        
except Exception as e:
    print(f"Direct espeak test failed: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 test_neptr_device.py
rm -f test_neptr_device.py
echo

# Test 7: Check audio permissions
echo "🧪 Test 7: Audio Permissions Check"
echo "Checking if user is in audio group:"
if groups | grep -q audio; then
    echo "✅ User is in audio group"
else
    echo "❌ User is NOT in audio group"
    echo "💡 Add user to audio group: sudo usermod -a -G audio $USER"
fi
echo

# Test 8: Check for audio conflicts
echo "🧪 Test 8: Audio Conflict Check"
echo "Checking for running audio processes:"
ps aux | grep -E "(pulseaudio|alsa|espeak)" | grep -v grep || echo "No audio processes found"
echo

echo "💡 Troubleshooting Steps:"
echo "1. If direct espeak-ng works but NEPTR doesn't:"
echo "   - Check NEPTR configuration in config.py"
echo "   - Verify AUDIO_FEEDBACK is True"
echo "   - Check if NEPTR is using the right audio device"
echo
echo "2. If NEPTR TTS function fails:"
echo "   - Check Python imports and dependencies"
echo "   - Verify espeak-ng is accessible from Python"
echo
echo "3. If audio permissions are the issue:"
echo "   - Add user to audio group: sudo usermod -a -G audio $USER"
echo "   - Log out and log back in"
echo
echo "4. If there are audio conflicts:"
echo "   - Kill conflicting processes"
echo "   - Restart audio services"
echo
echo "🚀 Next steps:"
echo "1. Run this script: ./debug_neptr_audio.sh"
echo "2. Check the output for any errors"
echo "3. Try the troubleshooting steps above"
echo "4. Test NEPTR again: python3 neptr.py"
