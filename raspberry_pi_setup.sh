#!/bin/bash

echo "🤖 NEPTR Raspberry Pi Easy Setup"
echo "================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  This script is designed for Raspberry Pi devices."
    echo "   It may work on other systems but is optimized for Pi."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "❌ Please don't run this script as root (sudo)."
    echo "   Run it as a regular user instead."
    exit 1
fi

echo "🚀 Starting NEPTR setup for Raspberry Pi..."
echo ""

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install package if not present
install_if_missing() {
    local package=$1
    local display_name=${2:-$1}
    
    if ! command_exists "$package"; then
        echo "📦 Installing $display_name..."
        sudo apt install -y "$package"
    else
        echo "✅ $display_name already installed"
    fi
}

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential system packages
echo ""
echo "🔧 Installing essential packages..."
install_if_missing "python3" "Python 3"
install_if_missing "python3-pip" "Python pip"
install_if_missing "python3-venv" "Python virtual environment"
install_if_missing "espeak-ng" "eSpeak text-to-speech"
install_if_missing "portaudio19-dev" "PortAudio development"
install_if_missing "python3-pyaudio" "PyAudio"
install_if_missing "git" "Git"
install_if_missing "wget" "Wget"
install_if_missing "unzip" "Unzip"

# Install additional useful packages for Pi
echo ""
echo "🍓 Installing Raspberry Pi specific packages..."
install_if_missing "python3-gpiozero" "GPIO library"
install_if_missing "python3-picamera2" "Camera library (if Pi Camera attached)"
install_if_missing "python3-rpi.gpio" "GPIO library (alternative)"

# Create project directory if not already there
if [ ! -d "$(pwd)/neptr_env" ]; then
    echo ""
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv neptr_env
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source neptr_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo ""
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create models directory and download speech model
echo ""
echo "📁 Setting up speech recognition..."
mkdir -p ~/models

if [ ! -d ~/models/vosk-model-small-en-us-0.15 ]; then
    echo "📥 Downloading speech recognition model..."
    cd ~/models
    wget -q --show-progress https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    cd - > /dev/null
    echo "✅ Speech model downloaded successfully"
else
    echo "✅ Speech recognition model already exists"
fi

# Set up audio permissions
echo ""
echo "🔊 Setting up audio permissions..."
sudo usermod -a -G audio $USER

# Create easy startup scripts
echo ""
echo "🚀 Creating startup scripts..."

# Main startup script
cat > start_neptr.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🤖 Starting NEPTR..."
source neptr_env/bin/activate
python3 neptr.py
EOF

# Quick test script
cat > test_neptr.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🧪 Testing NEPTR..."
source neptr_env/bin/activate
python3 tests/test_neptr.py
EOF

# Voice test script
cat > test_voice.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🎤 Testing voice..."
source neptr_env/bin/activate
python3 tests/test_voice.py
EOF

# Make scripts executable
chmod +x start_neptr.sh test_neptr.sh test_voice.sh

# Create systemd service for auto-start
echo ""
echo "⚙️  Creating systemd service for auto-start..."
cat > neptr.service << EOF
[Unit]
Description=NEPTR AI Assistant
After=network.target sound.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start_neptr.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create desktop shortcut
echo ""
echo "🖥️  Creating desktop shortcut..."
cat > NEPTR.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NEPTR AI Assistant
Comment=Voice-controlled AI assistant for Raspberry Pi
Exec=$(pwd)/start_neptr.sh
Icon=terminal
Terminal=true
Categories=Utility;AudioVideo;
EOF

# Create a simple config file
echo ""
echo "⚙️  Creating configuration file..."
cat > neptr_config.py << 'EOF'
# NEPTR Configuration for Raspberry Pi
# Edit these settings to customize your experience

# Voice Settings
VOICE_SPEED = 150  # Speed of speech (100-200)
VOICE_PITCH = 50   # Pitch of voice (0-100)

# Wake Word Settings
WAKE_PHRASES = [
    "hello neptr",
    "hey neptr", 
    "hi neptr",
    "neptr"
]

# Audio Settings
SAMPLE_RATE = 16000  # Lower for better Pi performance
CHUNK_SIZE = 1024    # Audio chunk size

# Performance Settings
USE_GPU = False      # Set to True if you have GPU acceleration
LOW_POWER_MODE = True  # Optimize for Pi performance

# Hardware Settings
ENABLE_LED = True    # Enable status LED (if connected)
ENABLE_BUTTON = False  # Enable physical button (if connected)
ENABLE_CAMERA = False  # Enable camera features (if connected)

print("🤖 NEPTR configuration loaded!")
EOF

# Create a simple status checker
cat > neptr_status.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🤖 NEPTR Status Check"
echo "===================="

# Check if virtual environment exists
if [ -d "neptr_env" ]; then
    echo "✅ Virtual environment: OK"
else
    echo "❌ Virtual environment: Missing"
fi

# Check if speech model exists
if [ -d ~/models/vosk-model-small-en-us-0.15 ]; then
    echo "✅ Speech model: OK"
else
    echo "❌ Speech model: Missing"
fi

# Check if main script exists
if [ -f "neptr.py" ]; then
    echo "✅ Main script: OK"
else
    echo "❌ Main script: Missing"
fi

# Check if requirements are installed
if [ -d "neptr_env" ]; then
    source neptr_env/bin/activate
    if python3 -c "import vosk, sounddevice, numpy" 2>/dev/null; then
        echo "✅ Python packages: OK"
    else
        echo "❌ Python packages: Missing"
    fi
    deactivate
fi

# Check audio permissions
if groups $USER | grep -q audio; then
    echo "✅ Audio permissions: OK"
else
    echo "❌ Audio permissions: Missing (reboot may be needed)"
fi

echo ""
echo "🎯 To start NEPTR: ./start_neptr.sh"
echo "🧪 To test: ./test_neptr.sh"
echo "🎤 To test voice: ./test_voice.sh"
EOF

chmod +x neptr_status.sh

# Create a simple update script
cat > update_neptr.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🔄 Updating NEPTR..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Update Python packages
echo "📚 Updating Python packages..."
source neptr_env/bin/activate
pip install --upgrade -r requirements.txt
deactivate

echo "✅ Update complete!"
echo "🤖 NEPTR is ready to use!"
EOF

chmod +x update_neptr.sh

echo ""
echo "🎉 Setup complete! NEPTR is ready to use!"
echo ""
echo "📋 What was created:"
echo "  • start_neptr.sh     - Start NEPTR"
echo "  • test_neptr.sh      - Test NEPTR"
echo "  • test_voice.sh      - Test voice features"
echo "  • neptr_status.sh    - Check system status"
echo "  • update_neptr.sh    - Update NEPTR"
echo "  • neptr_config.py    - Configuration file"
echo "  • neptr.service      - Auto-start service"
echo "  • NEPTR.desktop      - Desktop shortcut"
echo ""
echo "🚀 Quick Start:"
echo "  1. Test your installation: ./test_neptr.sh"
echo "  2. Start NEPTR: ./start_neptr.sh"
echo "  3. Check status: ./neptr_status.sh"
echo ""
echo "⚙️  Optional Auto-start:"
echo "  sudo cp neptr.service /etc/systemd/system/"
echo "  sudo systemctl enable neptr.service"
echo "  sudo systemctl start neptr.service"
echo ""
echo "🔑 OpenAI Setup (Optional):"
echo "  cp run_neptr_template.sh run_neptr.sh"
echo "  nano run_neptr.sh  # Add your API key"
echo "  chmod +x run_neptr.sh"
echo ""
echo "🤖 Say 'Hello Neptr' to wake me up!"
echo ""
echo "💡 Tip: Reboot your Pi to ensure all permissions are active!"
