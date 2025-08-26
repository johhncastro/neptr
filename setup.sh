#!/bin/bash

echo "🤖 Setting up NEPTR AI Assistant on Raspberry Pi..."
echo "=================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv espeak-ng portaudio19-dev python3-pyaudio

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv neptr_env
source neptr_env/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create models directory
echo "📁 Creating models directory..."
mkdir -p ~/models

# Download Vosk model if not already present
if [ ! -d ~/models/vosk-model-small-en-us-0.15 ]; then
    echo "📥 Downloading speech recognition model..."
    cd ~/models
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    cd -
else
    echo "✅ Speech recognition model already exists"
fi

# Set up audio permissions
echo "🔊 Setting up audio permissions..."
sudo usermod -a -G audio $USER

# Create a startup script
echo "🚀 Creating startup script..."
cat > start_neptr.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source neptr_env/bin/activate
python3 neptr.py
EOF

chmod +x start_neptr.sh

# Create systemd service for auto-start (optional)
echo "⚙️  Creating systemd service (optional)..."
cat > neptr.service << EOF
[Unit]
Description=NEPTR AI Assistant
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start_neptr.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Setup complete!"
echo ""
echo "🎉 NEPTR is ready to use!"
echo ""
echo "To test your installation:"
echo "  python3 test_neptr.py"
echo ""
echo "To start NEPTR manually:"
echo "  ./start_neptr.sh"
echo ""
echo "To enable auto-start on boot (optional):"
echo "  sudo cp neptr.service /etc/systemd/system/"
echo "  sudo systemctl enable neptr.service"
echo "  sudo systemctl start neptr.service"
echo ""
echo "To set up OpenAI integration (optional):"
echo "  export OPENAI_API_KEY='your-api-key-here'"
echo ""
echo "🤖 Say 'Hello Neptr' to wake me up!"
