import json, queue, sys, subprocess, os, shutil
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = os.path.expanduser("~/models/vosk-model-small-en-us-0.15")

# Include both "neptr" and common mishear ("nectar")
TRIGGERS = [
    "hello neptr", "hey neptr", "hi neptr",
    "hello nectar", "hey nectar", "hi nectar"
]

# Audio config
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000  # 0.5s chunks at 16kHz

if not os.path.isdir(MODEL_PATH):
    print("Vosk model not found at", MODEL_PATH)
    sys.exit(1)

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)

audio_q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_q.put(bytes(indata))

# Prefer espeak-ng if installed; otherwise use macOS 'say'
USE_ESPEAK = shutil.which("espeak-ng") is not None

def tts(text):
    if USE_ESPEAK:
        subprocess.run(["espeak-ng", "-s", "170", "-p", "40", "-v", "en-us", text], check=False)
    else:
        subprocess.run(["say", "-r", "170", text], check=False)

print('NEPTR is listening… say "hello neptr" (or "hey nectar")')

with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE,
                       dtype='int16', channels=1, callback=callback):
    while True:
        data = audio_q.get()
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            transcript = res.get("text", "").lower().strip()
            if transcript:
                print("Heard:", transcript)
                if any(kw in transcript for kw in TRIGGERS):
                    tts("Hello friend! I am nepter. How may I serve?")
        else:
            # For partials, you could read:
            # partial = json.loads(rec.PartialResult()).get("partial", "")
            pass
