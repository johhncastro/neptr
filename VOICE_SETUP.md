# 🎤 Neptr Voice Setup Guide

This guide shows you how to get Neptr's authentic voice from Adventure Time using OpenAI TTS.

## 🎯 **OpenAI TTS (Recommended - High Quality)**

OpenAI's TTS is included with your existing API key and provides excellent voice quality.

### Setup:
1. **Configure**: In `config.py`:
   ```python
   TTS_ENGINE = "openai"
   OPENAI_TTS_MODEL = "tts-1"
   OPENAI_TTS_VOICE = "alloy"  # Best for Neptr
   ```

### Voice Options:
- **alloy** - Deep, robotic (best for Neptr)
- **echo** - Deep, clear
- **fable** - Warm, friendly
- **onyx** - Deep, authoritative
- **nova** - Bright, energetic
- **shimmer** - Soft, gentle

## 🎯 **Option 2: Piper TTS (Local, Free)**

Piper runs locally and is completely free.

### Setup:
1. **Install Piper**: 
   ```bash
   # On macOS
   brew install piper-tts
   
   # Or download from: https://github.com/rhasspy/piper
   ```
2. **Download Model**: Get a deep voice model
3. **Configure**: In `config.py`:
   ```python
   TTS_ENGINE = "piper"
   ```

## 🎯 **Option 3: Enhanced espeak (Fallback)**

Improve the basic espeak voice for more robot-like sound.

### Setup:
1. **Configure**: In `config.py`:
   ```python
   TTS_ENGINE = "espeak"
   VOICE_SPEED = 150      # Slower for more robotic
   VOICE_PITCH = 25       # Lower for deeper voice
   VOICE_GAP = 8          # More gaps for robot effect
   ```

## 🎵 **Creating Neptr's Voice**

### For OpenAI TTS (Best Results):
1. **Try Different Voices**: Test all 6 OpenAI voices to find the best match
2. **Use "alloy"**: Deep, robotic voice that sounds most like Neptr
3. **Adjust Settings**: Fine-tune speed and pitch in config

### Voice Characteristics:
- **Deep, robotic tone**
- **Slight metallic quality**
- **Enthusiastic delivery**
- **Clear pronunciation**
- **Slight echo/reverb effect**

## 🛠️ **Quick Setup Commands**

### OpenAI TTS:
```bash
# Already included with your OpenAI API
# Just change TTS_ENGINE = "openai" in config.py
```

### Piper:
```bash
# Install piper-tts
# Download voice model
# Change TTS_ENGINE = "piper" in config.py
```

## 🎮 **Testing Your Voice**

```bash
# Test TTS engines
python3 tests/test_openai_tts.py

# Test all voice options
python3 tests/test_voice.py

# Run with new voice
./run_neptr.sh
```

## 💡 **Tips for Best Results**

1. **OpenAI**: Try different voices (alloy, echo, onyx) for best match
2. **Piper**: Download multiple models to find the best robotic voice
3. **espeak**: Adjust speed, pitch, and gaps for more robot-like sound

## 🔧 **Troubleshooting**

### OpenAI TTS Issues:
- Verify API key has TTS access
- Check internet connection
- Try different voice options

### Piper Issues:
- Ensure piper is installed correctly
- Check model file path
- Verify audio output works

## 🎯 **Recommended Setup**

For the best Neptr voice experience:

1. **Start with OpenAI TTS** (high quality, already paid for)
2. **Use Piper for offline** (free, local)
3. **espeak as final fallback** (always works)

Happy voice synthesizing! 🤖🥧
