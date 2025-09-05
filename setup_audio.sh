#!/bin/bash

# Audio Setup Script for Raspberry Pi with Jabra Speak 410
# This script will diagnose and configure audio for NEPTR

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Some operations may not work correctly."
        print_status "Consider running as regular user and using sudo when needed."
    fi
}

# Function to install required packages
install_packages() {
    print_header "Installing Required Packages"
    
    print_status "Updating package list..."
    sudo apt update
    
    packages=("alsa-utils" "espeak-ng" "pulseaudio" "pulseaudio-utils" "python3-pip")
    
    for package in "${packages[@]}"; do
        print_status "Installing $package..."
        if sudo apt install -y "$package"; then
            print_success "$package installed successfully"
        else
            print_error "Failed to install $package"
            return 1
        fi
    done
    
    print_success "All packages installed successfully"
    echo
}

# Function to diagnose system
diagnose_system() {
    print_header "System Diagnosis"
    
    # Check if running on Raspberry Pi
    if grep -q "arm" /proc/cpuinfo || grep -q "aarch64" /proc/cpuinfo; then
        print_success "Running on ARM architecture (Raspberry Pi)"
    else
        print_warning "Not running on ARM - this script is optimized for Raspberry Pi"
    fi
    
    # Check kernel version
    print_status "Kernel version: $(uname -r)"
    
    # Check available memory
    print_status "Available memory: $(free -h | grep '^Mem:' | awk '{print $7}')"
    
    echo
}

# Function to check USB devices
check_usb_devices() {
    print_header "USB Device Detection"
    
    print_status "Checking USB devices..."
    if command -v lsusb &> /dev/null; then
        usb_output=$(lsusb)
        echo "$usb_output"
        
        if echo "$usb_output" | grep -i "jabra\|speak" > /dev/null; then
            print_success "Jabra device detected in USB devices"
        else
            print_warning "No Jabra device found in USB list"
            print_status "Make sure the Jabra Speak 410 is connected and powered on"
        fi
    else
        print_error "lsusb command not found"
    fi
    
    echo
}

# Function to check audio devices
check_audio_devices() {
    print_header "Audio Device Detection"
    
    # Check ALSA cards
    print_status "ALSA Cards:"
    if [ -f /proc/asound/cards ]; then
        cat /proc/asound/cards
    else
        print_error "Cannot read ALSA cards"
    fi
    
    echo
    
    # Check playback devices
    print_status "Playback Devices (aplay -l):"
    if command -v aplay &> /dev/null; then
        aplay -l 2>/dev/null || print_error "aplay -l failed"
    else
        print_error "aplay command not found"
    fi
    
    echo
    
    # Check recording devices
    print_status "Recording Devices (arecord -l):"
    if command -v arecord &> /dev/null; then
        arecord -l 2>/dev/null || print_error "arecord -l failed"
    else
        print_error "arecord command not found"
    fi
    
    echo
}

# Function to check audio services
check_audio_services() {
    print_header "Audio Services Status"
    
    # Check if PulseAudio is running
    if pgrep pulseaudio > /dev/null; then
        print_success "PulseAudio is running"
    else
        print_warning "PulseAudio is not running"
        print_status "Starting PulseAudio..."
        pulseaudio --start 2>/dev/null || print_warning "Failed to start PulseAudio"
    fi
    
    # Check ALSA status
    if [ -d /proc/asound ]; then
        print_success "ALSA is available"
    else
        print_error "ALSA is not available"
    fi
    
    echo
}

# Function to test TTS
test_tts() {
    print_header "Text-to-Speech Testing"
    
    if command -v espeak-ng &> /dev/null; then
        print_success "espeak-ng is installed"
        print_status "Version: $(espeak-ng --version 2>&1 | head -1)"
        
        print_status "Testing TTS output..."
        if timeout 5 espeak-ng "Hello, this is a test of the Jabra speaker" 2>/dev/null; then
            print_success "TTS test completed successfully"
        else
            print_error "TTS test failed or timed out"
        fi
    else
        print_error "espeak-ng is not installed"
    fi
    
    echo
}

# Function to configure ALSA
configure_alsa() {
    print_header "ALSA Configuration"
    
    # Find the Jabra device card number
    jabra_card=$(aplay -l 2>/dev/null | grep -i "jabra\|speak\|usb" | head -1 | sed 's/card \([0-9]*\).*/\1/')
    
    if [ -n "$jabra_card" ]; then
        print_success "Found Jabra device on card $jabra_card"
        
        # Create ALSA configuration
        alsa_config="pcm.!default {
    type hw
    card $jabra_card
    device 0
}

ctl.!default {
    type hw
    card $jabra_card
}"
        
        print_status "Creating ALSA configuration..."
        echo "$alsa_config" > ~/.asoundrc
        print_success "ALSA configuration saved to ~/.asoundrc"
        
        # Test the configuration
        print_status "Testing ALSA configuration..."
        if aplay -D default /dev/zero 2>/dev/null & sleep 1; kill $! 2>/dev/null; then
            print_success "ALSA configuration test passed"
        else
            print_warning "ALSA configuration test failed"
        fi
    else
        print_warning "Could not find Jabra device in audio cards"
        print_status "You may need to manually configure the audio device"
    fi
    
    echo
}

# Function to configure PulseAudio
configure_pulseaudio() {
    print_header "PulseAudio Configuration"
    
    if command -v pactl &> /dev/null; then
        print_status "Available PulseAudio sinks:"
        pactl list short sinks 2>/dev/null || print_warning "Failed to list PulseAudio sinks"
        
        # Try to find Jabra device
        jabra_sink=$(pactl list short sinks 2>/dev/null | grep -i "jabra\|speak" | head -1 | awk '{print $2}')
        
        if [ -n "$jabra_sink" ]; then
            print_success "Found Jabra device: $jabra_sink"
            print_status "Setting as default sink..."
            pactl set-default-sink "$jabra_sink" 2>/dev/null && print_success "Default sink set to $jabra_sink"
        else
            print_warning "Could not find Jabra device in PulseAudio sinks"
        fi
    else
        print_warning "PulseAudio tools not available"
    fi
    
    echo
}

# Function to test audio output
test_audio_output() {
    print_header "Audio Output Testing"
    
    print_status "Testing audio output with various methods..."
    
    # Test 1: espeak-ng
    print_status "Test 1: espeak-ng"
    if timeout 3 espeak-ng "Hello from Raspberry Pi" 2>/dev/null; then
        print_success "espeak-ng test passed"
    else
        print_error "espeak-ng test failed"
    fi
    
    # Test 2: speaker-test
    print_status "Test 2: speaker-test"
    if timeout 3 speaker-test -t wav -c 2 -l 1 2>/dev/null; then
        print_success "speaker-test passed"
    else
        print_warning "speaker-test failed or not available"
    fi
    
    # Test 3: aplay with test file
    print_status "Test 3: aplay with test file"
    if [ -f /usr/share/sounds/alsa/Front_Left.wav ]; then
        if timeout 3 aplay /usr/share/sounds/alsa/Front_Left.wav 2>/dev/null; then
            print_success "aplay test passed"
        else
            print_error "aplay test failed"
        fi
    else
        print_warning "Test audio file not found"
    fi
    
    echo
}

# Function to set volume levels
set_volume() {
    print_header "Volume Configuration"
    
    print_status "Current volume levels:"
    if command -v amixer &> /dev/null; then
        amixer scontents 2>/dev/null || print_warning "Could not get volume levels"
    fi
    
    print_status "Setting volume to 80%..."
    if command -v amixer &> /dev/null; then
        amixer set Master 80% 2>/dev/null && print_success "Volume set to 80%"
    else
        print_warning "amixer not available"
    fi
    
    print_status "Unmuting audio..."
    if command -v amixer &> /dev/null; then
        amixer set Master unmute 2>/dev/null && print_success "Audio unmuted"
    else
        print_warning "amixer not available"
    fi
    
    echo
}

# Function to test NEPTR
test_neptr() {
    print_header "NEPTR Audio Test"
    
    if [ -f "neptr.py" ]; then
        print_status "NEPTR script found"
        print_status "Testing NEPTR TTS function..."
        
        # Create a simple test script
        cat > test_neptr_audio.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from neptr import tts
    print("Testing NEPTR TTS...")
    tts("Hello, this is a test of NEPTR's voice output")
    print("TTS test completed")
except Exception as e:
    print(f"TTS test failed: {e}")
EOF
        
        if python3 test_neptr_audio.py; then
            print_success "NEPTR TTS test passed"
        else
            print_error "NEPTR TTS test failed"
        fi
        
        # Clean up test file
        rm -f test_neptr_audio.py
    else
        print_warning "NEPTR script not found in current directory"
    fi
    
    echo
}

# Function to provide recommendations
provide_recommendations() {
    print_header "Recommendations and Next Steps"
    
    echo "If audio is still not working, try these steps:"
    echo
    echo "1. Hardware checks:"
    echo "   - Ensure Jabra Speak 410 is powered on"
    echo "   - Try a different USB port"
    echo "   - Check USB cable connection"
    echo
    echo "2. Software configuration:"
    echo "   - Reboot the system: sudo reboot"
    echo "   - Check volume levels: alsamixer"
    echo "   - Test with: espeak-ng 'Hello world'"
    echo
    echo "3. Manual configuration:"
    echo "   - Edit ~/.asoundrc for ALSA"
    echo "   - Use pavucontrol for PulseAudio GUI"
    echo "   - Check /etc/asound.conf for system-wide config"
    echo
    echo "4. For NEPTR specifically:"
    echo "   - Make sure espeak-ng is working"
    echo "   - Check that audio output is not muted"
    echo "   - Verify device is set as default"
    echo
    echo "5. Debugging commands:"
    echo "   - aplay -l                    # List playback devices"
    echo "   - arecord -l                  # List recording devices"
    echo "   - cat /proc/asound/cards      # List ALSA cards"
    echo "   - pactl list short sinks      # List PulseAudio sinks"
    echo "   - alsamixer                   # Audio mixer"
    echo
}

# Main execution
main() {
    print_header "Raspberry Pi Audio Setup for Jabra Speak 410"
    echo "This script will diagnose and configure audio for NEPTR"
    echo
    
    check_root
    
    # Run all diagnostic and configuration functions
    diagnose_system
    check_usb_devices
    check_audio_devices
    check_audio_services
    
    # Ask user if they want to install packages
    echo -e "${YELLOW}Do you want to install required packages? (y/n):${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        install_packages
    else
        print_status "Skipping package installation"
    fi
    
    test_tts
    configure_alsa
    configure_pulseaudio
    set_volume
    test_audio_output
    test_neptr
    provide_recommendations
    
    print_header "Audio Setup Complete"
    print_success "Audio setup script completed!"
    print_status "Try running NEPTR now: python3 neptr.py"
    echo
}

# Run main function
main "$@"
