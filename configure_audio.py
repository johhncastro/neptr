#!/usr/bin/env python3
"""
Audio configuration script for Raspberry Pi with Jabra Speak 410
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def configure_audio():
    """Configure audio for Jabra Speak 410"""
    print("🔧 Audio Configuration for Jabra Speak 410")
    print("=" * 50)
    print()
    
    # Check if running as root
    if os.geteuid() != 0:
        print("⚠️  This script needs to be run with sudo for some operations")
        print("   Run: sudo python3 configure_audio.py")
        print()
    
    # Install required packages
    print("📦 Installing required packages...")
    packages = ["alsa-utils", "espeak-ng", "pulseaudio", "pulseaudio-utils"]
    
    for package in packages:
        print(f"  📥 Installing {package}...")
        stdout, stderr, code = run_command(f"sudo apt update && sudo apt install -y {package}")
        if code == 0:
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
            print(f"  Error: {stderr}")
    print()
    
    # Check audio devices
    print("🎵 Checking audio devices...")
    stdout, stderr, code = run_command("aplay -l")
    if code == 0:
        print("  📱 Available audio devices:")
        print(stdout)
        
        # Look for Jabra device
        jabra_found = False
        for line in stdout.split('\n'):
            if 'jabra' in line.lower() or 'speak' in line.lower() or 'usb' in line.lower():
                print(f"  ✅ Found potential Jabra device: {line}")
                jabra_found = True
        
        if not jabra_found:
            print("  ⚠️  No Jabra device found in audio devices")
            print("  💡 Make sure the Jabra Speak 410 is connected and powered on")
    else:
        print("  ❌ Failed to list audio devices")
    print()
    
    # Set default audio device
    print("⚙️  Configuring default audio device...")
    
    # Create ALSA configuration
    alsa_config = """
# ALSA configuration for Jabra Speak 410
pcm.!default {
    type hw
    card 1
    device 0
}

ctl.!default {
    type hw
    card 1
}
"""
    
    try:
        with open("/tmp/.asoundrc", "w") as f:
            f.write(alsa_config)
        print("  ✅ Created ALSA configuration file")
        print("  💡 Copy to home directory: cp /tmp/.asoundrc ~/.asoundrc")
    except Exception as e:
        print(f"  ❌ Failed to create ALSA config: {e}")
    print()
    
    # Test audio output
    print("🔊 Testing audio output...")
    test_commands = [
        "espeak-ng 'Hello, this is a test of the Jabra speaker'",
        "aplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null || echo 'Test file not found'",
        "speaker-test -t wav -c 2 -l 1 2>/dev/null || echo 'Speaker test not available'"
    ]
    
    for cmd in test_commands:
        print(f"  🧪 Testing: {cmd.split()[0]}")
        stdout, stderr, code = run_command(f"timeout 5 {cmd}")
        if code == 0:
            print("  ✅ Test completed successfully")
        else:
            print("  ❌ Test failed or timed out")
    print()
    
    # Provide manual configuration steps
    print("📋 Manual Configuration Steps:")
    print("  1. Check if Jabra device is detected:")
    print("     lsusb | grep -i jabra")
    print()
    print("  2. List audio devices:")
    print("     aplay -l")
    print("     arecord -l")
    print()
    print("  3. Test audio output:")
    print("     espeak-ng 'Hello world'")
    print("     speaker-test -t wav -c 2 -l 1")
    print()
    print("  4. Set volume levels:")
    print("     alsamixer")
    print("     # Use arrow keys to adjust volume, F6 to select card")
    print()
    print("  5. Configure default device:")
    print("     # Edit ~/.asoundrc or /etc/asound.conf")
    print("     # Set card number to your Jabra device")
    print()
    print("  6. For NEPTR specifically:")
    print("     # Make sure espeak-ng is working")
    print("     # Check that audio output is not muted")
    print("     # Verify device is set as default")

if __name__ == "__main__":
    configure_audio()
