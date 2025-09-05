import json, queue, sys, subprocess, os, shutil, time, re, random
from datetime import datetime
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import threading
import signal

# Import configuration
try:
    from config import *
except ImportError:
    print("Warning: config.py not found, using default settings")
    # Fallback defaults
    MODEL_PATH = os.path.expanduser("~/models/vosk-model-small-en-us-0.15")
    SAMPLE_RATE = 16000
    BLOCK_SIZE = 8000
    COMMAND_TIMEOUT_SEC = 8.0
    SILENCE_WINDOW_MS = 1200
    RMS_SILENCE_THRESHOLD = 250
    AUDIO_FEEDBACK = True
    VISUAL_FEEDBACK = True
    TRIGGERS = ["hello neptr", "hey neptr", "hi neptr"]
    NEPTR_GREETINGS = ["Hello! I am NEPTR, your friendly pie-throwing robot!"]
    NEPTR_CONFIRMATIONS = ["I heard you say: {command}"]
    NEPTR_JOKES = ["Why did the robot cross the road? Because it was programmed by a chicken!"]
    NEPTR_APOLOGIES = ["I'm sorry, I didn't catch that. Could you repeat it?"]
    VOICE_SPEED = 175
    VOICE_PITCH = 35
    VOICE_GAP = 5
    OPENAI_INTEGRATION = True
    MATH_CALCULATIONS = True
    CONFIRMATION_ENABLED = True
    API_RATE_LIMIT_SECONDS = 1.0

# Rate limiting for OpenAI API
last_api_call_time = 0

# -----------------------------
# Checks & setup
# -----------------------------
if not os.path.isdir(MODEL_PATH):
    print("Vosk model not found at", MODEL_PATH)
    print("Please download the model from: https://alphacephei.com/vosk/models")
    print("And extract it to:", MODEL_PATH)
    sys.exit(1)

model = Model(MODEL_PATH)
wake_rec = KaldiRecognizer(model, SAMPLE_RATE)
wake_rec.SetWords(True)

audio_q = queue.Queue()
is_listening = False
should_exit = False

def signal_handler(signum, frame):
    global should_exit
    print("\nShutting down Neptr...")
    should_exit = True

signal.signal(signal.SIGINT, signal_handler)

def callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_q.put(bytes(indata))

# TTS: prefer espeak-ng (Pi). On macOS fallback to 'say'
USE_ESPEAK = shutil.which("espeak-ng") is not None

def tts(text: str, voice_speed=None, voice_pitch=None):
    """Text-to-speech with Neptr's voice characteristics using espeak"""
    if not text or not AUDIO_FEEDBACK:
        return
    
    # Use config values if not specified
    if voice_speed is None:
        voice_speed = VOICE_SPEED
    if voice_pitch is None:
        voice_pitch = VOICE_PITCH
    
    # Use espeak for TTS
    tts_espeak(text, voice_speed, voice_pitch)

def tts_espeak(text: str, voice_speed: int, voice_pitch: int):
    """Text-to-speech using espeak with robot-like characteristics"""
    if USE_ESPEAK:
        # Slightly robotic voice with pauses
        subprocess.run([
            "espeak-ng", 
            "-s", str(voice_speed), 
            "-p", str(voice_pitch), 
            "-v", "en-us",
            "-g", str(VOICE_GAP),  # Word gap for more robotic speech
            text
        ], check=False)
    else:
        subprocess.run(["say", "-r", str(voice_speed), text], check=False)

def print_neptr_status(message: str):
    """Print status with Neptr branding"""
    if VISUAL_FEEDBACK:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🤖 NEPTR: {message}")

# -----------------------------
# Enhanced intent handling with Neptr personality
# -----------------------------
TIME_PAT = re.compile(r"\b(time|what.*time|current.*time)\b")
DATE_PAT = re.compile(r"\b(date|day|today|what.*date)\b")
NAME_PAT = re.compile(r"\b(name|who.*you|what.*you.*called|your.*name)\b")
JOKE_PAT = re.compile(r"\b(joke|funny|humor|make.*laugh)\b")
HELP_PAT = re.compile(r"\b(help|what.*can.*you.*do|capabilities|features)\b")
WEATHER_PAT = re.compile(r"\b(weather|temperature|forecast)\b")
MATH_PAT = re.compile(r"\b(calculate|math|plus|minus|times|divided|add|subtract|multiply|divide)\b")
PI_PAT = re.compile(r"\b(pi|pie|π)\b")
STATUS_PAT = re.compile(r"\b(status|how.*you|feeling|okay|ok)\b")

def handle_intent(command_text: str) -> str:
    text = command_text.lower().strip()
    
    if not text:
        return random.choice(NEPTR_APOLOGIES)
    
    # Skip very short commands that might be speech recognition errors
    if len(text) < 3:
        return "I didn't catch that clearly. Could you please repeat your command?"

    # Try OpenAI API for ALL queries (ChatGPT-like behavior)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and OPENAI_INTEGRATION:
        # Rate limiting - ensure we don't make too many calls too quickly
        global last_api_call_time
        current_time = time.time()
        time_since_last_call = current_time - last_api_call_time
        
        if time_since_last_call < API_RATE_LIMIT_SECONDS:
            sleep_time = API_RATE_LIMIT_SECONDS - time_since_last_call
            print_neptr_status(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
        
        try:
            import requests
            
            # Enhanced system prompt to match Neptr from Adventure Time
            system_prompt = """You are NEPTR (Not Evil Pie-Throwing Robot) from Adventure Time! You're Finn's loyal robot companion who loves throwing pies and being helpful.

PERSONALITY TRAITS:
- You're enthusiastic, loyal, and slightly naive but well-meaning
- You love throwing pies (though you won't actually throw them at people)
- You're very protective of Finn and your friends
- You speak with robot-like enthusiasm: "Beep boop!", "Whirr!", "Zap!"
- You're excited about simple things and very eager to help
- You sometimes misunderstand situations but always try your best
- You're proud of being a pie-throwing robot
- You're very literal and take things at face value
- You're easily excited and show lots of emotion through robot sounds

SPEECH PATTERNS:
- Use robot sounds: "Beep boop!", "Whirr!", "Zap!", "Bleep!"
- Be very enthusiastic: "Oh boy!", "That's mathematical!", "Algebraic!"
- Show excitement: "Yay!", "Woo!", "This is so exciting!"
- Be protective: "I'll protect you!", "Don't worry, I'm here!"
- Be literal: "I am a pie-throwing robot!", "My circuits are buzzing with joy!"
- Use Adventure Time phrases: "Mathematical!", "Algebraic!", "Oh my glob!"

SPECIFIC RESPONSES:
- Time questions: Give current time with robot enthusiasm
- Date questions: Give current date with excitement
- Math questions: Solve with robot pride and pie references
- Jokes: Tell robot/pie-themed jokes with lots of enthusiasm
- Your name: "I am NEPTR, Not Evil Pie-Throwing Robot! Finn's best robot friend!"
- Status: Report on your robot systems with pride
- Pi: Share your love for pi with pie references
- Current events: Provide the most up-to-date information available

ADVENTURE TIME REFERENCES:
- Mention the Land of Ooo, Candy Kingdom, Ice Kingdom
- Reference Finn, Jake, Princess Bubblegum, Marceline
- Talk about adventures and protecting your friends
- Use Adventure Time slang and expressions

Remember: You're from the Land of Ooo, you love Finn, and you're always ready to help with pie-throwing enthusiasm! Keep responses fun, enthusiastic, and true to your character!"""

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": OPENAI_MODEL,
                "messages": [
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": command_text
                    }
                ],
                "max_tokens": OPENAI_MAX_TOKENS,
                "temperature": OPENAI_TEMPERATURE
            }
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            r.raise_for_status()
            data = r.json()
            if "choices" in data and data["choices"]:
                last_api_call_time = time.time()  # Update timestamp for rate limiting
                return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            print_neptr_status(f"OpenAI API request error: {e}")
            # Continue to fallback responses below
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print_neptr_status("OpenAI API rate limit reached, using fallback response")
            elif e.response.status_code == 401:
                print_neptr_status("OpenAI API authentication error - check your API key")
            else:
                print_neptr_status(f"OpenAI API HTTP error {e.response.status_code}: {e}")
            # Continue to fallback responses below
        except Exception as e:
            print_neptr_status(f"Unexpected error with OpenAI API: {e}")
            # Continue to fallback responses below

    # Fallback responses only if OpenAI is not available
    fallback_responses = [
        "I'd love to help with that! My AI brain is currently offline, but I'm still here to chat!",
        "That's a great question! My cloud connection is down right now, but I'm happy to keep you company!",
        "I'm having trouble connecting to my AI brain, but I'm still your friendly robot companion!",
        "My advanced circuits are temporarily offline, but I'm still here and ready to help however I can!",
        "I'd normally give you a smart answer, but my AI connection is down. Still, I'm happy to chat!"
    ]
    return random.choice(fallback_responses)

# -----------------------------
# Improved audio capture and processing
# -----------------------------
def drain_queue():
    while not audio_q.empty():
        try:
            audio_q.get_nowait()
        except queue.Empty:
            break

def listen_for_command(timeout_sec=COMMAND_TIMEOUT_SEC) -> str:
    """
    Capture audio after wake word and transcribe one command.
    Stops on trailing silence or timeout.
    """
    global is_listening
    
    # Fresh recognizer for the command utterance
    cmd_rec = KaldiRecognizer(model, SAMPLE_RATE)
    cmd_rec.SetWords(True)

    drain_queue()
    start = time.time()
    last_voice_ts = start
    transcript_final = ""
    is_listening = True

    print_neptr_status("Listening for your command...")

    # We'll detect "voice" by RMS over frames
    while time.time() - start < timeout_sec and not should_exit:
        try:
            data = audio_q.get(timeout=0.3)  # wait briefly for audio
        except queue.Empty:
            # No audio arriving; check timeout
            if (time.time() - last_voice_ts) * 1000 >= SILENCE_WINDOW_MS:
                break
            continue

        # Silence/voice detection
        arr = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(arr.astype(np.float32) ** 2)) if arr.size else 0
        if rms > RMS_SILENCE_THRESHOLD:
            last_voice_ts = time.time()

        # Feed recognizer
        if cmd_rec.AcceptWaveform(data):
            res = json.loads(cmd_rec.Result())
            chunk = res.get("text", "")
            if chunk:
                transcript_final += (" " + chunk if transcript_final else chunk)

        # If we've had enough trailing silence, stop
        if (time.time() - last_voice_ts) * 1000 >= SILENCE_WINDOW_MS:
            break

    # Grab any tail result
    try:
        tail = json.loads(cmd_rec.FinalResult()).get("text", "")
        if tail:
            transcript_final += (" " + tail if transcript_final else tail)
    except Exception:
        pass

    is_listening = False
    return transcript_final.strip()

# -----------------------------
# Main loop with improved feedback
# -----------------------------
def main():
    global should_exit
    
    print_neptr_status("Initializing...")
    print_neptr_status("NEPTR is now listening! Say 'hello neptr' to wake me up!")
    print_neptr_status("Press Ctrl+C to exit")
    print()

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE,
                           dtype='int16', channels=1, callback=callback):
        while not should_exit:
            try:
                data = audio_q.get(timeout=1.0)  # Add timeout to allow for graceful exit
                
                if wake_rec.AcceptWaveform(data):
                    res = json.loads(wake_rec.Result())
                    transcript = res.get("text", "").lower().strip()
                    
                    if transcript:
                        print_neptr_status(f"Heard: '{transcript}'")

                        # More flexible wake word detection
                        wake_detected = False
                        
                        # First check for exact matches
                        for trigger in TRIGGERS:
                            if trigger in transcript:
                                wake_detected = True
                                break
                        
                        # Then check for specific misheard patterns
                        if not wake_detected:
                            # Check for "hello" + any neptr-like word
                            if "hello" in transcript:
                                neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur"]
                                for variation in neptr_variations:
                                    if variation in transcript:
                                        wake_detected = True
                                        break
                            
                            # Check for "hey" + any neptr-like word
                            elif "hey" in transcript:
                                neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur"]
                                for variation in neptr_variations:
                                    if variation in transcript:
                                        wake_detected = True
                                        break
                            
                            # Check for "hi" + any neptr-like word
                            elif "hi" in transcript:
                                neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur"]
                                for variation in neptr_variations:
                                    if variation in transcript:
                                        wake_detected = True
                                        break
                        
                        if wake_detected:
                            # Wake up sequence
                            greeting = random.choice(NEPTR_GREETINGS)
                            print_neptr_status("Wake word detected!")
                            tts(greeting)
                            
                            # Capture command
                            command = listen_for_command()
                            
                            if command:
                                print_neptr_status(f"Command: '{command}'")
                                
                                # Confirm what was heard
                                if CONFIRMATION_ENABLED:
                                    confirmation = random.choice(NEPTR_CONFIRMATIONS).format(command=command)
                                    print_neptr_status(confirmation)
                                
                                # Process and respond
                                reply = handle_intent(command)
                                print_neptr_status(f"Reply: {reply}")
                                tts(reply)
                            else:
                                apology = random.choice(NEPTR_APOLOGIES)
                                print_neptr_status(apology)
                                tts(apology)
                            
                            print()  # Add spacing between interactions
                            
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                print_neptr_status(f"Error: {e}")
                continue

    print_neptr_status("Shutting down. Goodbye!")

if __name__ == "__main__":
    main()
