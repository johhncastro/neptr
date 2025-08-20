# NEPTR (Never-Ending Pie-Throwing Robot) 🤖

A mini **NEPTR** from the tv show adventure time that talks back when you say **“Hello NEPTR.”**  
This is a **short, basic checklist** to get v1 (voice-only) off the ground.

This process is currently being recorded and will be uploaded on my youtube channel.

---

## ✅ Current Status
- [x] **Raspberry Pi 4 Model B (4 GB)**
- [x] **Arduino Uno**
- [x] **Rough STL** for future sheet-metal body
- [x] microSD (32–64 GB) + USB reader
- [ ] Pi 4 power supply (5 V / 3 A) + small heatsink/fan
- [x] **USB speakerphone** (Jabra Speak 410) for mic + speaker
- [x] Breadboard + jumper wires
- [ ] 2× WS2812B (“NeoPixel”) LEDs + 330–470 Ω resistor + 1000 µF cap
- [ ] 16 mm momentary button (press-to-talk)


---

## 🛠️ Near-Term To-Dos (Voice MVP)
- [ ] Flash **Raspberry Pi OS (Bookworm)** to microSD and boot
- [ ] `sudo apt update && sudo apt full-upgrade -y`
- [ ] Plug in Jabra → verify audio with `arecord -l` / `aplay -l`
- [ ] Install deps: `python3-pip portaudio19-dev espeak-ng`
- [ ] `pip3 install vosk sounddevice simpleaudio`
- [ ] Download **Vosk small en-US** model to `~/models/...`
- [ ] Run minimal loop (`neptr.py`): detect “hello neptr” → speak reply
- [ ] (Optional) Add `systemd` service to auto-start on boot

---

## 🎯 Short Roadmap
- **Stage 1:** Voice loop (wake phrase → STT → reply → TTS)  
- **Stage 2:** Personality (better TTS with Piper, LEDs for eyes, button)  
- **Stage 3:** Body (sheet-metal fit, mounts, grille)  
- **Stage 4:** Motion (motors, driver, battery; Arduino assists)

---


## [View 3D Model](./stl-files/3d-chassis-rough.stl)
