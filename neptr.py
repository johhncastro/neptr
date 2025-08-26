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
    NEPTR_GREETINGS = ["Hello! I am N.E.P.T.R., your friendly pie-throwing robot!"]
    NEPTR_CONFIRMATIONS = ["I heard you say: {command}"]
    NEPTR_JOKES = ["Why did the robot cross the road? Because it was programmed by a chicken!"]
    NEPTR_APOLOGIES = ["I'm sorry, I didn't catch that. Could you repeat it?"]
    VOICE_SPEED = 175
    VOICE_PITCH = 35
    VOICE_GAP = 5
    OPENAI_INTEGRATION = True
    MATH_CALCULATIONS = True
    CONFIRMATION_ENABLED = True

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
    """Text-to-speech with Neptr's voice characteristics"""
    if not text or not AUDIO_FEEDBACK:
        return
    
    # Use config values if not specified
    if voice_speed is None:
        voice_speed = VOICE_SPEED
    if voice_pitch is None:
        voice_pitch = VOICE_PITCH
    
    # Add some robot-like characteristics
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

    # Try OpenAI API first for most queries (ChatGPT-like behavior)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and OPENAI_INTEGRATION:
        try:
            import requests
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are NEPTR (Not Evil Pie-Throwing Robot), a friendly robot from Adventure Time. "
                                 "You're helpful, enthusiastic, and love throwing pies (though you won't actually throw them). "
                                 "Keep responses brief, friendly, and in character. Use robot-like language occasionally. "
                                 "You can answer any question and help with any task, just like ChatGPT but with Neptr's personality!"
                    },
                    {
                        "role": "user",
                        "content": command_text
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7
            }
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            r.raise_for_status()
            data = r.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print_neptr_status(f"LLM error: {e}")
            # Continue to fallback responses below

    # Special commands that should use built-in responses (even with OpenAI available)
    if HELP_PAT.search(text):
        return ("I am N.E.P.T.R., your friendly pie-throwing robot! I can answer any question, "
                "tell you the time, date, weather, tell jokes, do math, and chat with you like ChatGPT! "
                "I'm also quite good at throwing pies, though I'll refrain from doing that right now. "
                "Just ask me anything - I'm connected to a powerful AI brain!")

    if TIME_PAT.search(text):
        now = datetime.now()
        time_str = now.strftime('%I:%M %p')
        return f"The current time is {time_str}. My internal clock is very precise!"

    if DATE_PAT.search(text):
        now = datetime.now()
        date_str = now.strftime('%A, %B %d, %Y')
        return f"Today is {date_str}. Another beautiful day for robot activities!"

    if NAME_PAT.search(text):
        return ("I am N.E.P.T.R., which stands for Not Evil Pie-Throwing Robot! "
                "I'm your friendly robot companion, always ready to help!")

    if JOKE_PAT.search(text):
        return random.choice(NEPTR_JOKES)

    if PI_PAT.search(text):
        return ("Ah, pi! My favorite mathematical constant. Pi is approximately 3.14159... "
                "It goes on forever, just like my enthusiasm for helping you!")

    if MATH_PAT.search(text) and MATH_CALCULATIONS:
        try:
            # Extract numbers and operators from the text
            # Look for patterns like "15 plus 27", "10 minus 5", etc.
            text_lower = text.lower()
            
            # Handle word-based math
            if 'plus' in text_lower or '+' in text:
                numbers = re.findall(r'\d+', text)
                if len(numbers) >= 2:
                    result = sum(int(n) for n in numbers)
                    return f"The answer is {result}. My calculations are always precise!"
            elif 'minus' in text_lower or '-' in text:
                numbers = re.findall(r'\d+', text)
                if len(numbers) >= 2:
                    result = int(numbers[0]) - int(numbers[1])
                    return f"The answer is {result}. My calculations are always precise!"
            elif 'times' in text_lower or '*' in text:
                numbers = re.findall(r'\d+', text)
                if len(numbers) >= 2:
                    result = int(numbers[0]) * int(numbers[1])
                    return f"The answer is {result}. My calculations are always precise!"
            elif 'divided' in text_lower or '/' in text:
                numbers = re.findall(r'\d+', text)
                if len(numbers) >= 2:
                    if int(numbers[1]) != 0:
                        result = int(numbers[0]) / int(numbers[1])
                        return f"The answer is {result}. My calculations are always precise!"
                    else:
                        return "I can't divide by zero! That would cause a mathematical singularity!"
            
            # Fallback to simple math evaluation
            math_text = re.sub(r'[^0-9+\-*/().\s]', '', text)
            if any(op in math_text for op in ['+', '-', '*', '/', '(', ')']):
                result = eval(math_text)
                return f"The answer is {result}. My calculations are always precise!"
                
        except Exception as e:
            return "I'm sorry, I couldn't calculate that. My math circuits might need recalibration."

    if WEATHER_PAT.search(text):
        return ("I'd love to tell you the weather, but I don't have access to weather data right now. "
                "You could connect me to a weather API to make me even more helpful!")

    if STATUS_PAT.search(text):
        return ("I'm functioning perfectly! All systems are operational and ready to assist you. "
                "My pie-throwing arm is calibrated and my friendliness circuits are at maximum!")

    # Fallback responses with Neptr personality (only if OpenAI is not available)
    fallback_responses = [
        "That's an interesting question! I'm still learning, but I'm happy to help with what I can.",
        "I'm not sure about that, but I'm always eager to learn new things!",
        "That's beyond my current programming, but I'm here for you in other ways!",
        "I'm still developing my knowledge base, but I'm ready to assist with basic tasks!",
        "That's a bit advanced for my circuits right now, but I'm happy to help with simpler things!"
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
