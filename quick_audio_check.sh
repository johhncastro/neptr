#!/bin/bash

# Quick Audio Check Script for Raspberry Pi with Jabra Speak 410
# Run this first to get a quick overview of your audio setup

echo "🔊 Quick Audio Check for Jabra Speak 410"
echo "========================================"
echo

# Check if Jabra is connected
echo "📱 USB Device Check:"
if lsusb | grep -i "jabra\|speak" > /dev/null; then
    echo "✅ Jabra device detected"
    lsusb | grep -i "jabra\|speak"
else
    echo "❌ No Jabra device found"
    echo "💡 Make sure the Jabra Speak 410 is connected and powered on"
fi
echo

# Check audio devices
echo "🎵 Audio Devices:"
if command -v aplay &> /dev/null; then
    echo "Playback devices:"
    aplay -l 2>/dev/null || echo "❌ No playback devices found"
else
    echo "❌ aplay command not found"
fi
echo

# Check espeak-ng
echo "🗣️  TTS Software:"
if command -v espeak-ng &> /dev/null; then
    echo "✅ espeak-ng is installed"
    echo "🧪 Testing TTS..."
    timeout 3 espeak-ng "Hello, this is a test" 2>/dev/null && echo "✅ TTS test passed" || echo "❌ TTS test failed"
else
    echo "❌ espeak-ng is not installed"
    echo "💡 Install with: sudo apt install espeak-ng"
fi
echo

# Check volume
echo "🔊 Volume Check:"
if command -v amixer &> /dev/null; then
    volume=$(amixer get Master 2>/dev/null | grep -o '[0-9]*%' | head -1)
    if [ -n "$volume" ]; then
        echo "📊 Master volume: $volume"
    else
        echo "❌ Could not get volume level"
    fi
else
    echo "❌ amixer command not found"
fi
echo

echo "💡 Next steps:"
echo "1. If Jabra not detected: Check USB connection and power"
echo "2. If no audio devices: Run full setup: ./setup_audio.sh"
echo "3. If espeak-ng missing: sudo apt install espeak-ng"
echo "4. If TTS fails: Check volume levels and audio configuration"
echo
echo "🚀 Run full setup: ./setup_audio.sh"
