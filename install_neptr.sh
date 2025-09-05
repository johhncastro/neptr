#!/bin/bash

echo "🤖 NEPTR Complete Raspberry Pi Installer"
echo "========================================="
echo ""

# Check if we're on a Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  This installer is optimized for Raspberry Pi"
    echo "   It will work on other systems but may not be optimal."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check OS version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "🖥️  Detected OS: $PRETTY_NAME"
    if [[ "$VERSION_ID" == "12" ]] && [[ "$ID" == "debian" ]]; then
        echo "✅ Optimized for Bookworm Lite OS!"
    fi
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "❌ Please don't run this as root (sudo)."
    echo "   Run it as a regular user instead."
    exit 1
fi

# Set installation directory
INSTALL_DIR="$HOME/neptr"
REPO_URL="https://github.com/johhncastro/neptr.git"

echo "🚀 Installing NEPTR on your Raspberry Pi..."
echo "   This will download the complete NEPTR repository and set everything up!"
echo "   Installation directory: $INSTALL_DIR"
echo "   This will take a few minutes. Grab a snack! 🍕"
echo ""

# Check if neptr directory already exists
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  NEPTR directory already exists at $INSTALL_DIR"
    read -p "Do you want to remove it and reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    else
        echo "❌ Installation cancelled."
        exit 1
    fi
fi

# Function to show progress
show_progress() {
    local message=$1
    echo "📋 $message"
}

# Download NEPTR repository
show_progress "Downloading NEPTR repository..."
git clone "$REPO_URL" "$INSTALL_DIR"
if [ $? -ne 0 ]; then
    echo "❌ Failed to download NEPTR repository!"
    echo "   Please check your internet connection and try again."
    exit 1
fi

# Change to installation directory
cd "$INSTALL_DIR"

# Update system
show_progress "Updating system packages..."
sudo apt update -qq && sudo apt upgrade -y -qq

# Install all dependencies in one go (optimized for Bookworm Lite)
show_progress "Installing system dependencies..."
sudo apt install -y -qq python3-pip python3-venv espeak-ng portaudio19-dev python3-pyaudio git wget unzip python3-gpiozero python3-dev build-essential

# Bookworm Lite specific optimizations
show_progress "Optimizing for Bookworm Lite OS..."
# Ensure audio group exists
sudo groupadd -f audio
# Add user to audio group
sudo usermod -a -G audio $USER

# Create virtual environment
show_progress "Setting up Python environment..."
python3 -m venv neptr_env -q
source neptr_env/bin/activate

# Install Python packages
show_progress "Installing Python packages..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Download speech model
show_progress "Downloading speech recognition model..."
mkdir -p ~/models
cd ~/models
if [ ! -d vosk-model-small-en-us-0.15 ]; then
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
fi
cd - > /dev/null

# Audio permissions already set up above

# Create all the helper scripts
show_progress "Creating helper scripts..."

# Startup script
cat > start_neptr.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🤖 Starting NEPTR..."
source neptr_env/bin/activate
python3 neptr.py
EOF

# Test script
cat > test_neptr.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🧪 Testing NEPTR..."
source neptr_env/bin/activate
python3 tests/test_neptr.py
EOF

# Status checker
cat > neptr_status.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🤖 NEPTR Status Check"
echo "===================="

if [ -d "neptr_env" ]; then echo "✅ Virtual environment: OK"; else echo "❌ Virtual environment: Missing"; fi
if [ -d ~/models/vosk-model-small-en-us-0.15 ]; then echo "✅ Speech model: OK"; else echo "❌ Speech model: Missing"; fi
if [ -f "neptr.py" ]; then echo "✅ Main script: OK"; else echo "❌ Main script: Missing"; fi

if [ -d "neptr_env" ]; then
    source neptr_env/bin/activate
    if python3 -c "import vosk, sounddevice, numpy" 2>/dev/null; then
        echo "✅ Python packages: OK"
    else
        echo "❌ Python packages: Missing"
    fi
    deactivate
fi

if groups $USER | grep -q audio; then
    echo "✅ Audio permissions: OK"
else
    echo "❌ Audio permissions: Missing (reboot may be needed)"
fi

echo ""
echo "🎯 To start NEPTR: ./start_neptr.sh"
echo "🧪 To test: ./test_neptr.sh"
EOF

# Make scripts executable
chmod +x start_neptr.sh test_neptr.sh neptr_status.sh

# Create desktop shortcut
cat > NEPTR.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NEPTR AI Assistant
Comment=Voice-controlled AI assistant for Raspberry Pi
Exec=$INSTALL_DIR/start_neptr.sh
Icon=terminal
Terminal=true
Categories=Utility;AudioVideo;
EOF

# Move desktop shortcut to user's desktop
if [ -d "$HOME/Desktop" ]; then
    mv NEPTR.desktop "$HOME/Desktop/"
    echo "📱 Desktop shortcut created!"
fi

echo ""
echo "🎉 Installation complete! NEPTR is ready to use!"
echo ""
echo "📁 NEPTR installed in: $INSTALL_DIR"
echo ""
echo "🚀 Quick Start:"
echo "  cd $INSTALL_DIR"
echo "  1. Test: ./test_neptr.sh"
echo "  2. Start: ./start_neptr.sh"
echo "  3. Status: ./neptr_status.sh"
echo ""
echo "🔑 Optional OpenAI Setup:"
echo "  cd $INSTALL_DIR"
echo "  cp run_neptr_template.sh run_neptr.sh"
echo "  nano run_neptr.sh  # Add your API key"
echo "  chmod +x run_neptr.sh"
echo ""
echo "🤖 Say 'Hello Neptr' to wake me up!"
echo ""
echo "💡 Tip: Reboot your Pi to ensure all permissions are active!"
echo "   sudo reboot"
echo ""
echo "🔄 To update NEPTR in the future:"
echo "  cd $INSTALL_DIR && git pull"
