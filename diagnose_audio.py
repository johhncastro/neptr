#!/usr/bin/env python3
"""
Audio diagnostic script for Raspberry Pi with Jabra Speak 410
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

def diagnose_audio():
    """Diagnose audio setup on Raspberry Pi"""
    print("🔊 Raspberry Pi Audio Diagnostic Tool")
    print("=" * 50)
    print()
    
    # Check if we're on Raspberry Pi
    print("📋 System Information:")
    stdout, stderr, code = run_command("uname -a")
    if "arm" in stdout.lower() or "aarch64" in stdout.lower():
        print("  ✅ Running on ARM architecture (Raspberry Pi)")
    else:
        print("  ⚠️  Not running on ARM - this script is for Raspberry Pi")
    print()
    
    # Check audio devices
    print("🎤 Audio Devices:")
    stdout, stderr, code = run_command("aplay -l")
    if code == 0:
        print("  📱 ALSA Playback Devices:")
        print(stdout)
    else:
        print("  ❌ aplay -l failed")
        print(f"  Error: {stderr}")
    print()
    
    # Check recording devices
    stdout, stderr, code = run_command("arecord -l")
    if code == 0:
        print("  🎙️  ALSA Recording Devices:")
        print(stdout)
    else:
        print("  ❌ arecord -l failed")
        print(f"  Error: {stderr}")
    print()
    
    # Check USB devices
    print("🔌 USB Devices:")
    stdout, stderr, code = run_command("lsusb")
    if code == 0:
        print("  📱 USB Devices:")
        jabra_found = False
        for line in stdout.split('\n'):
            if 'jabra' in line.lower() or 'speak' in line.lower():
                print(f"  ✅ Jabra device found: {line}")
                jabra_found = True
        if not jabra_found:
            print("  ⚠️  No Jabra device detected in USB list")
            print("  📱 All USB devices:")
            for line in stdout.split('\n'):
                if line.strip():
                    print(f"    {line}")
    else:
        print("  ❌ lsusb failed")
    print()
    
    # Check audio configuration
    print("⚙️  Audio Configuration:")
    stdout, stderr, code = run_command("cat /proc/asound/cards")
    if code == 0:
        print("  🎵 ALSA Cards:")
        print(stdout)
    else:
        print("  ❌ Failed to read ALSA cards")
    print()
    
    # Check if pulseaudio is running
    stdout, stderr, code = run_command("pgrep pulseaudio")
    if code == 0:
        print("  ✅ PulseAudio is running")
    else:
        print("  ⚠️  PulseAudio is not running")
    print()
    
    # Check default audio device
    stdout, stderr, code = run_command("aplay -D default /dev/zero 2>&1 | head -5")
    if code == 0:
        print("  ✅ Default audio device test passed")
    else:
        print("  ❌ Default audio device test failed")
        print(f"  Error: {stderr}")
    print()
    
    # Check espeak installation
    print("🗣️  TTS Software:")
    stdout, stderr, code = run_command("which espeak-ng")
    if code == 0:
        print("  ✅ espeak-ng is installed")
        stdout, stderr, code = run_command("espeak-ng --version")
        if code == 0:
            print(f"  📋 Version: {stdout.split()[1] if len(stdout.split()) > 1 else 'Unknown'}")
    else:
        print("  ❌ espeak-ng is not installed")
        print("  💡 Install with: sudo apt install espeak-ng")
    print()
    
    # Test audio output
    print("🔊 Audio Output Test:")
    print("  🧪 Testing audio output...")
    stdout, stderr, code = run_command("timeout 3 espeak-ng 'Hello, this is a test' 2>&1")
    if code == 0:
        print("  ✅ espeak-ng test completed successfully")
    else:
        print("  ❌ espeak-ng test failed")
        print(f"  Error: {stderr}")
    print()
    
    # Provide recommendations
    print("💡 Recommendations:")
    print("  1. If Jabra device not detected:")
    print("     - Check USB connection")
    print("     - Try different USB port")
    print("     - Check if device is powered on")
    print()
    print("  2. If audio devices not showing:")
    print("     - Install ALSA utils: sudo apt install alsa-utils")
    print("     - Reboot the system")
    print()
    print("  3. If espeak-ng not working:")
    print("     - Install: sudo apt install espeak-ng")
    print("     - Test: espeak-ng 'Hello world'")
    print()
    print("  4. For Jabra Speak 410 specifically:")
    print("     - Device should appear as USB audio device")
    print("     - May need to set as default audio device")
    print("     - Check volume levels on device and system")

if __name__ == "__main__":
    diagnose_audio()
