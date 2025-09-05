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

## ⚡ What Happens During Installation

The installer automatically:
- ✅ Updates your Pi's system packages
- ✅ Installs all required dependencies
- ✅ Sets up Python virtual environment
- ✅ Downloads speech recognition model
- ✅ Configures audio permissions
- ✅ Creates easy-to-use startup scripts
- ✅ Adds desktop shortcut

## 🎯 After Installation

### 1. Test Your Setup
```bash
./test_neptr.sh
```

### 2. Start NEPTR
```bash
./start_neptr.sh
```

### 3. Check Status
```bash
./neptr_status.sh
```

## 🔑 Optional OpenAI Setup

For advanced AI conversations:

```bash
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
# Enable the service
sudo cp neptr.service /etc/systemd/system/
sudo systemctl enable neptr.service
sudo systemctl start neptr.service

# Check status
sudo systemctl status neptr.service
```

## 🎨 Customization

Edit `neptr_config.py` to customize:
- Voice speed and pitch
- Wake phrases
- Performance settings
- Hardware features

## 📱 Desktop Shortcut

A desktop icon was created automatically. Double-click to start NEPTR!

## 🆘 Need Help?

- Check the main README.md for detailed information
- Run `./neptr_status.sh` to diagnose issues
- Ensure your Pi has enough free space (at least 2GB)

---

**🎉 That's it! Your Pi is now a friendly robot companion!**

Say "Hello Neptr" and start chatting! 🤖🥧
