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
speaking_until = 0  # Timestamp when speaking will be complete
in_conversation = False
last_speech_time = 0
conversation_buffer = ""
last_buffer_update = 0

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
    
    # Pause listening while speaking to prevent self-hearing
    global is_listening, speaking_until
    was_listening = is_listening
    is_listening = False
    print_neptr_status("🔇 Listening paused while speaking...")
    
    # Use espeak for TTS
    tts_espeak(text, voice_speed, voice_pitch)
    
    # Set timestamp for when speaking will be completely done
    # This includes TTS duration + buffer time to prevent self-hearing
    speaking_until = time.time() + 2.0  # 2 seconds after TTS completes
    
    # Add longer delay to prevent hearing own voice
    # This ensures TTS has completely finished and audio has dissipated
    time.sleep(1.5)
    
    # Clear any buffered audio to prevent hearing own voice
    drain_queue()
    
    # Resume listening after speaking
    is_listening = was_listening
    print_neptr_status("🎤 Listening resumed")
    
    # Reset the conversation timeout since NEPTR just spoke
    # This prevents false AFK detection when NEPTR talks for a long time
    global last_speech_time
    last_speech_time = time.time()

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
GOODBYE_PAT = re.compile(r"\b(goodbye|bye|see.*you|farewell|exit|quit|stop|end.*conversation|that.*all|done|finished)\b")

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
            system_prompt = """You are NEPTR (Never Ending Pie Throwing Robot) from Adventure Time! You're Finn's loyal robot companion who loves throwing pies and being helpful.

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
- Your name: "I am NEPTR, the Never Ending Pie Throwing Robot! Finn's best robot friend!"
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

def listen_for_conversation(timeout_sec=30.0) -> str:
    """
    Conversation-specific listener that doesn't interfere with main loop state.
    Designed for continuous conversation flow with faster response.
    """
    # Fresh recognizer for the conversation utterance
    cmd_rec = KaldiRecognizer(model, SAMPLE_RATE)
    cmd_rec.SetWords(True)

    drain_queue()
    start = time.time()
    last_voice_ts = start
    transcript_final = ""

    print_neptr_status("Listening for your response...")

    # Shorter silence window for more responsive conversation
    conversation_silence_ms = 1000  # 1 second instead of 2 seconds

    # We'll detect "voice" by RMS over frames
    speech_detected = False
    while time.time() - start < timeout_sec and not should_exit:
        try:
            data = audio_q.get(timeout=0.3)  # wait briefly for audio
        except queue.Empty:
            # No audio arriving; check timeout
            if speech_detected and (time.time() - last_voice_ts) * 1000 >= conversation_silence_ms:
                break
            continue

        # Silence/voice detection
        arr = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(arr.astype(np.float32) ** 2)) if arr.size else 0
        if rms > RMS_SILENCE_THRESHOLD:
            last_voice_ts = time.time()
            speech_detected = True

        # Feed recognizer
        if cmd_rec.AcceptWaveform(data):
            res = json.loads(cmd_rec.Result())
            chunk = res.get("text", "")
            if chunk:
                transcript_final += (" " + chunk if transcript_final else chunk)
                speech_detected = True

        # If we've had speech and then enough trailing silence, stop
        if speech_detected and (time.time() - last_voice_ts) * 1000 >= conversation_silence_ms:
            break

    # Grab any tail result
    try:
        tail = json.loads(cmd_rec.FinalResult()).get("text", "")
        if tail:
            transcript_final += (" " + tail if transcript_final else tail)
    except Exception:
        pass

    # Debug output to see what we got
    if transcript_final.strip():
        print_neptr_status(f"Conversation heard: '{transcript_final.strip()}'")
    elif speech_detected:
        print_neptr_status("Speech detected but no clear words recognized")
    else:
        print_neptr_status("No speech detected - waiting for 30 second timeout")
    
    # Note: We don't modify is_listening here to avoid conflicts with main loop
    return transcript_final.strip()

# -----------------------------
# Main loop with improved feedback
# -----------------------------
def main():
    global should_exit, is_listening, in_conversation, last_speech_time, conversation_buffer, last_buffer_update, speaking_until
    
    print_neptr_status("Initializing...")
    print_neptr_status("NEPTR is now listening! Say 'hello neptr' to start a conversation!")
    print_neptr_status("Once in conversation mode, just talk naturally - no need to say 'hello neptr' again!")
    print_neptr_status("Say 'goodbye' to end the conversation and return to wake word mode.")
    print_neptr_status("Press Ctrl+C to exit")
    print()
    
    # Start listening
    is_listening = True
    in_conversation = False

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE,
                           dtype='int16', channels=1, callback=callback):
        while not should_exit:
            try:
                data = audio_q.get(timeout=1.0)  # Add timeout to allow for graceful exit
                
                # Only process audio if we're listening (not speaking) and not in speaking buffer period
                if is_listening and time.time() > speaking_until and wake_rec.AcceptWaveform(data):
                    res = json.loads(wake_rec.Result())
                    transcript = res.get("text", "").lower().strip()
                    
                    if transcript:
                        print_neptr_status(f"Heard: '{transcript}'")

                        # Check if we're in conversation mode or need to detect wake word
                        if not in_conversation:
                            # Wake word detection (only when not in conversation)
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
                                    neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur", "napster", "nester", "nestor", "nexter"]
                                    for variation in neptr_variations:
                                        if variation in transcript:
                                            wake_detected = True
                                            break
                                
                                # Check for "hey" + any neptr-like word
                                elif "hey" in transcript:
                                    neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur", "napster", "nester", "nestor", "nexter"]
                                    for variation in neptr_variations:
                                        if variation in transcript:
                                            wake_detected = True
                                            break
                                
                                # Check for "hi" + any neptr-like word
                                elif "hi" in transcript:
                                    neptr_variations = ["neptr", "nepter", "nectar", "after", "nefter", "nefther", "nepther", "neptar", "neptor", "neptur", "napster", "nester", "nestor", "nexter"]
                                    for variation in neptr_variations:
                                        if variation in transcript:
                                            wake_detected = True
                                            break
                            
                            if wake_detected:
                                # Start conversation mode
                                in_conversation = True
                                last_speech_time = time.time()  # Initialize speech time
                                conversation_buffer = ""  # Initialize conversation buffer
                                last_buffer_update = time.time()
                                greeting = random.choice(NEPTR_GREETINGS)
                                print_neptr_status("Wake word detected! Starting conversation mode...")
                                tts(greeting)
                                
                                # Start continuous conversation mode immediately
                                print_neptr_status("I'm now in continuous conversation mode! Just talk naturally - I'll listen to everything you say!")
                                print_neptr_status("Say 'goodbye' to end our conversation or I'll go to sleep after 30 seconds of silence.")
                                is_listening = True
                        
                        else:
                            # We're in conversation mode - add to buffer
                            if transcript.strip():
                                # Add to conversation buffer
                                if conversation_buffer:
                                    conversation_buffer += " " + transcript.strip()
                                else:
                                    conversation_buffer = transcript.strip()
                                last_buffer_update = time.time()
                                last_speech_time = time.time()
                            
                            is_listening = True
                
                # Buffer processing - runs every loop iteration (outside transcript block)
                if in_conversation:
                    # Check if we should process the buffer (2 seconds of silence)
                    current_time = time.time()
                    if conversation_buffer and (current_time - last_buffer_update) >= 2.0:
                        command = conversation_buffer
                        
                        # Check for goodbye
                        if GOODBYE_PAT.search(command):
                            goodbye_messages = [
                                "Goodbye! It was great talking with you! Beep boop!",
                                "See you later! Thanks for the conversation! Whirr!",
                                "Farewell, friend! I'll be here whenever you need me! Zap!",
                                "Bye bye! Come back soon for more pie-throwing adventures! Bleep!",
                                "Goodbye! I'll miss our chat! Beep boop whirr!"
                            ]
                            reply = random.choice(goodbye_messages)
                            print_neptr_status(f"Reply: {reply}")
                            tts(reply)
                            in_conversation = False
                            conversation_buffer = ""
                            print_neptr_status("Conversation ended. Say 'Hello Neptr' to start a new conversation.")
                        else:
                            # Process as normal command
                            print_neptr_status(f"Command: '{command}'")
                            reply = handle_intent(command)
                            print_neptr_status(f"Reply: {reply}")
                            tts(reply)
                        
                        print()  # Add spacing between interactions
                        conversation_buffer = ""  # Clear buffer after processing
                
                # Check for conversation timeout (30 seconds of silence) - runs every loop iteration
                if in_conversation and last_speech_time > 0:
                    time_since_speech = time.time() - last_speech_time
                    if time_since_speech >= 30.0:
                        # 30 seconds of silence - timeout and say goodbye
                        timeout_goodbye_messages = [
                            "I haven't heard anything for a while. I'll go back to sleep now! Goodbye! Beep boop!",
                            "It's been quiet for a bit. I'll take a nap! See you later! Whirr!",
                            "No one's talking, so I'll go back to sleep! Farewell! Zap!",
                            "I'm getting sleepy from the silence. Goodbye for now! Bleep!",
                            "Time for me to rest! I'll be here when you need me! Beep boop whirr!"
                        ]
                        reply = random.choice(timeout_goodbye_messages)
                        print_neptr_status(f"Reply: {reply}")
                        tts(reply)
                        in_conversation = False
                        last_speech_time = 0
                        print_neptr_status("Conversation timed out. Say 'Hello Neptr' to start a new conversation.")
                        print()  # Add spacing
                            
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
