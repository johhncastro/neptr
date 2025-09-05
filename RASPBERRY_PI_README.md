# 🤖 NEPTR Raspberry Pi Setup Guide

**The easiest way to get NEPTR running on your Raspberry Pi!**

## 🚀 One-Command Installation

Just copy and paste this single command into your Pi's terminal:

```bash
curl -sSL https://raw.githubusercontent.com/johhncastro/neptr/main/install_neptr.sh | bash
```

**Or download and run manually:**

```bash
# Download the installer
wget https://raw.githubusercontent.com/johhncastro/neptr/main/install_neptr.sh

# Make it executable
chmod +x install_neptr.sh

# Run it!
./install_neptr.sh
```

## 📋 What You Need

- **Raspberry Pi 4** (2GB RAM minimum, 4GB recommended)
- **Microphone** (USB or built-in)
- **Speakers/Headphones** 
- **Internet connection** for initial setup
- **Optional**: OpenAI API key for advanced features

### 🖥️ Supported Operating Systems

- **Raspberry Pi OS Bookworm Lite** (Recommended)
- **Raspberry Pi OS Bookworm Desktop**
- **Ubuntu 22.04+ for Raspberry Pi**
- **Other Debian-based distributions**

The installer is specifically optimized for **Bookworm Lite OS** and will detect your system automatically.

## ⚡ What Happens During Installation

The installer automatically:
- ✅ **Downloads NEPTR repository** from GitHub to `~/neptr`
- ✅ **Updates your Pi's system packages** for optimal performance
- ✅ **Installs all required dependencies** (Python, audio, build tools)
- ✅ **Sets up Python virtual environment** with all packages
- ✅ **Downloads speech recognition model** (Vosk)
- ✅ **Configures audio permissions** for microphone access
- ✅ **Creates easy-to-use startup scripts** (`start_neptr.sh`, `test_neptr.sh`, `neptr_status.sh`)
- ✅ **Adds desktop shortcut** for easy access
- ✅ **Optimizes for Bookworm Lite OS** with specific configurations

## 🎯 After Installation

### 1. Navigate to NEPTR Directory
```bash
cd ~/neptr
```

### 2. Test Your Setup
```bash
./test_neptr.sh
```

### 3. Start NEPTR
```bash
./start_neptr.sh
```

### 4. Check Status
```bash
./neptr_status.sh
```

## 🔑 Optional OpenAI Setup

For advanced AI conversations:

```bash
# Navigate to NEPTR directory
cd ~/neptr

# Copy the template
cp run_neptr_template.sh run_neptr.sh

# Edit with your API key
nano run_neptr.sh

# Make it executable
chmod +x run_neptr.sh
```

## 🎤 Using NEPTR

1. **Wake up**: Say "Hello Neptr"
2. **Give commands**: Ask questions, tell jokes, get the time
3. **Chat**: Have conversations with Neptr's personality

## 🛠️ Troubleshooting

### Audio Not Working?
```bash
# Navigate to NEPTR directory
cd ~/neptr

# Check status
./neptr_status.sh

# Reboot to activate permissions
sudo reboot
```

### Wake Word Not Detected?
- Speak clearly at normal volume
- Try: "Hey Neptr", "Hi Neptr", "Neptr"
- Check microphone levels in Pi settings

### Performance Issues?
- Close other applications
- Use headphones instead of speakers
- Ensure Pi has good ventilation

## 🔄 Updates

Keep NEPTR updated:

```bash
# Navigate to NEPTR directory
cd ~/neptr

# Update NEPTR code from GitHub
git pull

# Update system and packages
sudo apt update && sudo apt upgrade

# Update Python packages
source neptr_env/bin/activate
pip install --upgrade -r requirements.txt
deactivate
```

## 🎮 Auto-Start on Boot

Want NEPTR to start automatically when you turn on your Pi?

```bash
# Navigate to NEPTR directory
cd ~/neptr

# Enable the service
sudo cp neptr.service /etc/systemd/system/
sudo systemctl enable neptr.service
sudo systemctl start neptr.service

# Check status
sudo systemctl status neptr.service
```

## 🎨 Customization

Edit `config.py` to customize:
- Voice speed and pitch
- Wake phrases
- Performance settings
- Hardware features

```bash
# Navigate to NEPTR directory
cd ~/neptr

# Edit configuration
nano config.py
```

## 📱 Desktop Shortcut

A desktop icon was created automatically. Double-click to start NEPTR!

## 🆘 Need Help?

- Check the main README.md for detailed information
- Navigate to NEPTR directory: `cd ~/neptr`
- Run `./neptr_status.sh` to diagnose issues
- Ensure your Pi has enough free space (at least 2GB)
- For Bookworm Lite OS issues, check system logs: `journalctl -u neptr.service`

---

**🎉 That's it! Your Pi is now a friendly robot companion!**

Say "Hello Neptr" and start chatting! 🤖🥧
