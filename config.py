# NEPTR AI Assistant Configuration
# Edit these settings to customize your Neptr experience
import os

# ============================================================================
# AUDIO SETTINGS
# ============================================================================

# Speech recognition settings
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000  # 0.5s chunks at 16kHz

# Command listening parameters
COMMAND_TIMEOUT_SEC = 8.0           # max time to wait for a command
SILENCE_WINDOW_MS = 1200            # stop if this much trailing silence
RMS_SILENCE_THRESHOLD = 250         # adjust if it cuts off/never stops

# Voice settings
VOICE_SPEED = 175                   # Speech speed (words per minute)
VOICE_PITCH = 35                    # Voice pitch (0-99, lower = deeper)
VOICE_GAP = 5                       # Word gap for robotic speech

# TTS Engine settings
TTS_ENGINE = "openai"               # "espeak", "openai", "piper"
OPENAI_TTS_MODEL = "tts-1"          # OpenAI TTS model
OPENAI_TTS_VOICE = "alloy"          # "alloy", "echo", "fable", "onyx", "nova", "shimmer"

# ============================================================================
# WAKE WORD SETTINGS
# ============================================================================

# Wake phrases (include common mishears and Neptr-specific variations)
TRIGGERS = [
    # Standard variations
    "hello neptr", "hey neptr", "hi neptr", "neptr", "nepter",
    "hello nectar", "hey nectar", "hi nectar", "nectar",
    "wake up neptr", "neptr wake up", "activate neptr",
    "hello robot", "hey robot", "robot assistant",
    
    # Common mishears for "hello neptr"
    "hello after", "hello nefter", "hello nefther", "hello nefter",
    "hello nepther", "hello neptar", "hello neptor", "hello neptur",
    "hello neptir", "hello neptor", "hello neptar", "hello neptur",
    "hello neptir", "hello neptor", "hello neptar", "hello neptur",
    "hello neptir", "hello neptor", "hello neptar", "hello neptur",
    
    # Common mishears for "hey neptr"
    "hey after", "hey nefter", "hey nefther", "hey nefter",
    "hey nepther", "hey neptar", "hey neptor", "hey neptur",
    "hey neptir", "hey neptor", "hey neptar", "hey neptur",
    
    # Common mishears for "hi neptr"
    "hi after", "hi nefter", "hi nefther", "hi nefter",
    "hi nepther", "hi neptar", "hi neptor", "hi neptur",
    "hi neptir", "hi neptor", "hi neptar", "hi neptur",
    
    # Partial matches (more lenient)
    "neptr", "nepter", "nectar", "neptar", "neptor", "neptur",
    "nefter", "nefther", "nepther", "neptir",
    
    # Robot variations
    "hello robot", "hey robot", "hi robot",
    "hello assistant", "hey assistant", "hi assistant",
    "wake up neptr", "activate neptr", "start neptr",
    
    # Short variations (only when clearly intended)
    "neptr", "nepter", "nectar"
]

# ============================================================================
# PERSONALITY SETTINGS
# ============================================================================

# Neptr's personality responses
NEPTR_GREETINGS = [
    "Hello! I am N.E.P.T.R., your friendly pie-throwing robot!",
    "Greetings! N.E.P.T.R. at your service!",
    "Hello there! Ready to help with whatever you need!",
    "Hi! I'm Neptr, your robot companion!",
    "Greetings, friend! How can I assist you today?"
]

NEPTR_CONFIRMATIONS = [
    "I heard you say: {command}",
    "You said: {command}",
    "I understood: {command}",
    "Got it: {command}"
]

NEPTR_JOKES = [
    "Why did the robot cross the road? Because it was programmed by a chicken!",
    "What do you call a robot that likes to throw pies? A Neptr!",
    "Why don't robots like to go outside? Because they're afraid of getting a virus!",
    "What's a robot's favorite type of music? Heavy metal!",
    "Why did the robot go to the doctor? Because it had a byte!",
    "What do you call a robot that's always late? A slow-bot!",
    "Why did the robot go to the library? To check out some bytes!",
    "What's a robot's favorite dessert? Pi!",
    "Why don't robots like to play hide and seek? Because they always get caught in the cache!",
    "What do you call a robot that's good at math? A calculator!"
]

NEPTR_APOLOGIES = [
    "I'm sorry, I didn't catch that. Could you repeat it?",
    "I didn't quite understand. Can you say that again?",
    "My audio receptors might be malfunctioning. Could you repeat?",
    "I'm having trouble processing that. One more time?",
    "Sorry, my circuits are a bit fuzzy. Can you repeat?"
]

# ============================================================================
# FEATURE TOGGLES
# ============================================================================

# Enable/disable features
AUDIO_FEEDBACK = True               # Enable/disable audio feedback
VISUAL_FEEDBACK = True              # Enable/disable visual feedback
OPENAI_INTEGRATION = True           # Enable/disable OpenAI integration (primary response method)
MATH_CALCULATIONS = False           # Disabled - now handled by OpenAI
WEATHER_FEATURES = False            # Enable/disable weather features

# ============================================================================
# API SETTINGS
# ============================================================================

# OpenAI settings (optional)
OPENAI_MODEL = "gpt-4o"             # Model to use for responses (more current info)
OPENAI_MAX_TOKENS = 300             # Maximum response length
OPENAI_TEMPERATURE = 0.8            # Response creativity (0.0-1.0) - more creative
API_RATE_LIMIT_SECONDS = 1.0        # Minimum seconds between API calls

# Weather API settings (optional)
WEATHER_API_KEY = None              # Set your weather API key here
WEATHER_LOCATION = "auto"           # "auto" for IP-based location or "city,country"

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================

# Model path
MODEL_PATH = os.path.expanduser("~/models/vosk-model-small-en-us-0.15")

# Logging settings
LOG_LEVEL = "INFO"                  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = False                 # Enable/disable file logging
LOG_FILE = "neptr.log"              # Log file name

# Performance settings
USE_VIRTUAL_ENV = True              # Use virtual environment
AUTO_RESTART = True                 # Auto-restart on errors
RESTART_DELAY = 10                  # Seconds to wait before restart

# ============================================================================
# HARDWARE SETTINGS (for future use)
# ============================================================================

# LED settings (if you add status LEDs)
LED_ENABLED = False                 # Enable/disable LED feedback
LED_PIN = 18                        # GPIO pin for status LED
LED_BRIGHTNESS = 0.5                # LED brightness (0.0-1.0)

# Button settings (if you add a physical button)
BUTTON_ENABLED = False              # Enable/disable button
BUTTON_PIN = 17                     # GPIO pin for button
BUTTON_PULL_UP = True               # Use pull-up resistor

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Speech recognition sensitivity
WAKE_WORD_SENSITIVITY = 0.8         # Sensitivity for wake word (0.0-1.0)
COMMAND_SENSITIVITY = 0.7           # Sensitivity for commands (0.0-1.0)

# Audio processing
NOISE_REDUCTION = True              # Enable noise reduction
ECHO_CANCELLATION = True            # Enable echo cancellation
AUTOMATIC_GAIN_CONTROL = True       # Enable automatic gain control

# Response customization
RESPONSE_DELAY = 0.5                # Delay before responding (seconds)
CONFIRMATION_ENABLED = True         # Confirm what was heard
CONFIDENCE_THRESHOLD = 0.6          # Minimum confidence for responses
