import json, queue, sys, subprocess, os
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = os.path.expanduser("~/models/vosk-model-small-en-us-0.15")
TRIGGERS = ["hello neptr", "hey neptr", "hi neptr"]

# Select your default audio device, or set by index:
# print(sd.query_devices())  # to inspect devices
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

def tts(text):
    # Simple TTS; upgrade to Piper later for better quality
    subprocess.run(["espeak-ng", "-s", "170", "-p", "40", "-v", "en-us", text])

print("NEPTR is listening… say 'hello neptr'")

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
                    tts("Hello friend! I am N E P T R. How may I serve?")
        else:
            # Partial results stream here if you want responsiveness:
            # partial = json.loads(rec.PartialResult()).get("partial", "")
            pass


