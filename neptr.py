import json, queue, sys, subprocess, os, shutil, time, re
from datetime import datetime
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# -----------------------------
# Config
# -----------------------------
MODEL_PATH = os.path.expanduser("~/models/vosk-model-small-en-us-0.15")

# Wake phrases (include common mishears)
TRIGGERS = [
    "hello neptr", "hey neptr", "hi neptr",
    "hello nectar", "hey nectar", "hi nectar"
]

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000  # 0.5s chunks at 16kHz

# Command listening parameters
COMMAND_TIMEOUT_SEC = 6.0           # max time to wait for a command
SILENCE_WINDOW_MS = 900             # stop if this much trailing silence
RMS_SILENCE_THRESHOLD = 300         # adjust if it cuts off/never stops

# -----------------------------
# Checks & setup
# -----------------------------
if not os.path.isdir(MODEL_PATH):
    print("Vosk model not found at", MODEL_PATH)
    sys.exit(1)

model = Model(MODEL_PATH)
wake_rec = KaldiRecognizer(model, SAMPLE_RATE)
wake_rec.SetWords(True)

audio_q = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_q.put(bytes(indata))

# TTS: prefer espeak-ng (Pi). On macOS fallback to 'say'
USE_ESPEAK = shutil.which("espeak-ng") is not None

def tts(text: str):
    if not text:
        return
    if USE_ESPEAK:
        # Tune speed/pitch to preference
        subprocess.run(["espeak-ng", "-s", "175", "-p", "35", "-v", "en-us", text], check=False)
    else:
        subprocess.run(["say", "-r", "175", text], check=False)

# -----------------------------
# Simple intent handling
# -----------------------------
TIME_PAT = re.compile(r"\b(time|what.*time)\b")
DATE_PAT = re.compile(r"\b(date|day|today)\b")
NAME_PAT = re.compile(r"\b(name|who.*you|what.*you.*called)\b")
JOKE_PAT = re.compile(r"\b(joke|funny)\b")
HELP_PAT = re.compile(r"\b(help|what.*can.*you.*do)\b")

def handle_intent(command_text: str) -> str:
    text = command_text.lower().strip()
    if not text:
        return "I didn't hear a command."

    if HELP_PAT.search(text):
        return ("I can tell the time or date, introduce myself, or tell a joke. "
                "Try: what time is it, what's the date, what's your name, or tell me a joke.")

    if TIME_PAT.search(text):
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')}."
    if DATE_PAT.search(text):
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."
    if NAME_PAT.search(text):
        return "I am N.E.P.T.R., Not Evil Pie-Throwing Robot."
    if JOKE_PAT.search(text):
        return "Why did the robot cross the road? Because it was programmed by a chicken."


    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            import requests
            # Minimal example with OpenAI Responses API; adjust to your model/endpoint.
            # This is intentionally short and generic; replace with your preferred LLM call.
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "input": f"You are NEPTR, a friendly robot. User said: '{command_text}'. Reply briefly and helpfully."
            }
            r = requests.post("https://api.openai.com/v1/responses", headers=headers, json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            # The 'output_text' helper is available in many SDKs; for raw REST we pull from the first output item:
            # Fall back to something sane if schema changes.
            out = None
            if "output" in data and isinstance(data["output"], list) and data["output"]:
                first = data["output"][0]
                out = first.get("content", "")
            if not out:
                out = "Sorry, I couldn't think of a good answer."
            return out
        except Exception as e:
            print("LLM error:", e)
            return "Sorry, my brain link is down."
    else:
        return "I can handle time, date, name, and jokes. For other questions, connect my cloud brain later."

# -----------------------------
# Helpers to capture a single command after wake word
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
    # Fresh recognizer for the command utterance
    cmd_rec = KaldiRecognizer(model, SAMPLE_RATE)
    cmd_rec.SetWords(True)

    drain_queue()
    start = time.time()
    last_voice_ts = start
    transcript_final = ""

    # We'll detect "voice" by RMS over frames
    while time.time() - start < timeout_sec:
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
        else:

            pass

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

    return transcript_final.strip()

# -----------------------------
# Main loop
# -----------------------------
print('NEPTR is listening… say "hello neptr" (or "hey nectar")')

with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE,
                       dtype='int16', channels=1, callback=callback):
    while True:
        data = audio_q.get()
        if wake_rec.AcceptWaveform(data):
            res = json.loads(wake_rec.Result())
            transcript = res.get("text", "").lower().strip()
            if transcript:
                print("Heard:", transcript)

                if any(kw in transcript for kw in TRIGGERS):
                    tts("Hello friend. I am listening.")
                    # Capture one command utterance
                    command = listen_for_command()
                    print("Command:", command if command else "<none>")
                    if not command:
                        tts("I didn't hear a command.")
                        continue
                    # Decide and reply
                    reply = handle_intent(command)
                    print("Reply:", reply)
                    tts(reply)
        else:

            pass
