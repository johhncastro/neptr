# 🤖 NEPTR AI Assistant

A voice-controlled AI assistant inspired by Neptr from Adventure Time, designed to run on Raspberry Pi 4. NEPTR (Not Evil Pie-Throwing Robot) is your friendly robot companion that responds to voice commands with personality and enthusiasm!

## ✨ Features

- **Voice Wake Word Detection**: Say "Hello Neptr" to activate
- **Speech Recognition**: Converts your voice to text using Vosk
- **Text-to-Speech**: Responds with a robotic voice using espeak-ng
- **Neptr Personality**: Friendly, enthusiastic responses in character
- **Multiple Commands**: Time, date, jokes, math, weather, and more
- **OpenAI Integration**: Optional cloud brain for advanced conversations
- **Raspberry Pi Optimized**: Designed specifically for Pi 4 performance

## 🎯 What NEPTR Can Do

### Basic Commands
- **Time**: "What time is it?"
- **Date**: "What's the date today?"
- **Name**: "What's your name?"
- **Jokes**: "Tell me a joke"
- **Status**: "How are you feeling?"
- **Math**: "Calculate 15 plus 27"
- **Pi**: "Tell me about pi"

### Advanced Features
- **OpenAI Integration**: Ask complex questions (requires API key)
- **Weather**: Get weather information (requires API setup)
- **Conversation**: Chat naturally with Neptr's personality

## 🚀 Quick Setup

### Prerequisites
- Raspberry Pi 4 (2GB RAM minimum, 4GB recommended)
- Microphone and speakers/headphones
- Internet connection for initial setup

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd neptr
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start NEPTR**
   ```bash
   ./start_neptr.sh
   ```

### Manual Setup (Alternative)

If you prefer manual installation:

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv espeak-ng portaudio19-dev python3-pyaudio
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv neptr_env
   source neptr_env/bin/activate
   ```

3. **Install Python packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download speech model**
   ```bash
   mkdir -p ~/models
   cd ~/models
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   rm vosk-model-small-en-us-0.15.zip
   ```

## ⚙️ Configuration

### Environment Variables

Set these in your shell or add to `~/.bashrc`:

```bash
# For OpenAI integration (optional)
export OPENAI_API_KEY="your-openai-api-key-here"

# For weather API (optional)
export WEATHER_API_KEY="your-weather-api-key-here"
```

### Customization

Edit `neptr.py` to customize:

- **Wake phrases**: Modify the `TRIGGERS` list
- **Voice settings**: Adjust `voice_speed` and `voice_pitch` in the `tts()` function
- **Personality**: Add more responses to the various response lists
- **Commands**: Add new intent patterns and handlers

## 🎮 Usage

### Basic Usage
1. Run the assistant: `./start_neptr.sh`
2. Say "Hello Neptr" to wake it up
3. Speak your command clearly
4. Listen to Neptr's response

### Example Interactions

```
You: "Hello Neptr"
Neptr: "Hello! I am N.E.P.T.R., your friendly pie-throwing robot!"

You: "What time is it?"
Neptr: "The current time is 2:30 PM. My internal clock is very precise!"

You: "Tell me a joke"
Neptr: "Why did the robot cross the road? Because it was programmed by a chicken!"

You: "Calculate 15 plus 27"
Neptr: "The answer is 42. My calculations are always precise!"
```

## 🔧 Troubleshooting

### Common Issues

**"Vosk model not found"**
- Run the setup script again
- Manually download the model from https://alphacephei.com/vosk/models

**"No module named 'sounddevice'"**
- Activate the virtual environment: `source neptr_env/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Audio not working**
- Check microphone permissions: `sudo usermod -a -G audio $USER`
- Reboot: `sudo reboot`
- Test audio: `arecord -d 5 test.wav && aplay test.wav`

**Wake word not detected**
- Speak clearly and at normal volume
- Try different wake phrases: "Hey Neptr", "Hi Neptr", "Neptr"
- Check microphone levels in system settings

### Performance Tips

- **Reduce CPU usage**: Lower `SAMPLE_RATE` to 8000 (less accurate but faster)
- **Faster responses**: Use a smaller Vosk model
- **Better accuracy**: Use a larger Vosk model (more CPU intensive)

## 🎨 Customization Ideas

### Hardware Additions
- **LED indicators**: Add status LEDs for wake word detection
- **Physical button**: Add a push button for manual activation
- **Display**: Add a small LCD screen for visual feedback
- **Servo motors**: Add moving parts for more robot-like behavior

### Software Enhancements
- **Music player**: Add Spotify/MP3 playback capabilities
- **Home automation**: Integrate with smart home devices
- **Reminders**: Add calendar and reminder functionality
- **Voice training**: Improve wake word detection with custom training

## 📝 License

This project is open source. Feel free to modify and distribute!

## 🤝 Contributing

Contributions are welcome! Some ideas:
- Add new commands and capabilities
- Improve speech recognition accuracy
- Add more personality responses
- Create hardware integration guides
- Optimize for different Raspberry Pi models

## 🙏 Acknowledgments

- **Vosk**: Speech recognition engine
- **espeak-ng**: Text-to-speech synthesis
- **Adventure Time**: Inspiration for Neptr's character
- **Raspberry Pi Foundation**: For making this possible

---

**Remember**: NEPTR is Not Evil Pie-Throwing Robot - friendly, helpful, and always ready to assist! 🤖🥧
