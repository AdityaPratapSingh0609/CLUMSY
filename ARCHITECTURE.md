# DESKBOT — Cute Physical Avatar & Distributed Mesh Architecture

## 1. Vision & Hardware-Software Philosophy

DESKBOT is a **cute, physical, 3D-printed desktop companion robot** combined with a **distributed local computing mesh**.

* **The Physical Robot (The Cute Avatar):**
  A compact, expressive desktop companion powered by a microcontroller (such as an **ESP32** or **Arduino with BLE/Wi-Fi**). It features:
  - **Animated Eyes / Display:** Mini OLED/LCD (e.g., dual SSD1306 or round GC9A01 displays) showing expressive facial animations (blinking, happy, listening, thinking, sleepy).
  - **Expressive Motors:** Micro-servos (e.g., SG90) driving head pan/tilt, ear wiggles, or body nods.
  - **Audio I/O:** Built-in microphone and speaker/buzzer to listen and speak.
  - **Connectivity:** Bluetooth (BLE / Classic) and Wi-Fi to tether directly to the mesh.

* **The Host Station (The Desktop Brain):**
  Microcontrollers only have kilobytes to a few megabytes of RAM and cannot host heavy LLMs directly. The robot **offloads memory and compute to your desktop/laptop** over a local peer-to-peer Bluetooth/Wi-Fi mesh:
  - Your desktop acts as the **Brain & Memory Bank** (holding the GGUF LLM, Whisper STT, Piper TTS, and context).
  - The desktop computes decisions and streams back **robot telemetry** (motor positions, eye expressions, synthesized audio) in real time.
  - The desktop controls other connected devices (phones, laptops, apps) upon voice/gesture request.

---

## 2. Distributed Mesh Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PHYSICAL AVATAR (Cute Desk Robot)                    │
│   Microcontroller: ESP32 / Arduino Nano ESP32                         │
│   - OLED / LCD: Expressive eyes (Blink, Happy, Confused, Focused)      │
│   - Servos: 2-DOF Head Pan/Tilt & Expressive Gestures                  │
│   - Audio: I2S Digital Mic (INMP441) + Amp (MAX98357A) + Speaker       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 
                       Bluetooth (BLE/Serial) or Local Wi-Fi
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  DESKTOP CORE (The Brain & Memory Base)                │
│   Runs locally on your PC / Desktop                                    │
│   - Event Bus & State Machine (Idle, Listening, Thinking, Responding)  │
│   - Offline STT (faster-whisper)                                       │
│   - Offline Local Brain (llama.cpp / Qwen 2.5 / Llama 3.2 GGUF)        │
│   - Offline TTS (Piper TTS)                                            │
│   - Robot Motion & Expression Generator (maps emotions to servo/OLED)  │
└──────────────┬──────────────────────────────────────────┬──────────────┘
               │ Local Wi-Fi / Bluetooth                  │ Bluetooth / Wi-Fi
               ▼                                          ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│        LAPTOP AGENT          │          │        PHONE AGENT           │
│  - Remote app launcher       │          │  - Notification relay        │
│  - System controls (volume)  │          │  - Battery & sensor telemetry│
│  - Media & window manager    │          │  - Trigger phone actions     │
└──────────────────────────────┘          └──────────────────────────────┘
```

---

## 3. Physical Hardware Components (Recommended BOM)

| Component | Recommended Part | Purpose | Approx. Cost |
| :--- | :--- | :--- | :--- |
| **Brain Microcontroller** | **ESP32-S3** (or Arduino Nano ESP32) | Built-in Wi-Fi, Bluetooth 5 (BLE), dual-core, native USB & hardware PWM for servos | ~$4 - $6 |
| **Expressive Eyes** | **0.96" or 1.3" I2C OLED (SSD1306)** or **1.28" Round LCD (GC9A01)** | Renders vector eye animations (blinking, eye-roll, happy squint) | ~$2 - $5 |
| **Expressive Motors** | 2x **SG90 or MG90S Micro Servos** | Pan (left/right) and Tilt (up/down nodding/tilting) | ~$3 - $5 |
| **Microphone** | **INMP441 I2S Digital Mic** | Low-noise, clean digital audio capture | ~$1.50 |
| **Speaker / Audio** | **MAX98357A I2S DAC Amp + 3W mini speaker** | Clear voice response output | ~$3 |
| **Chassis** | **3D-Printed cute enclosure** (STL files) | Aesthetic shell (e.g. desktop pet, mini astronaut, or retro TV shape) | Filament |

---

## 4. Robot Emotion & Motion Protocol

The Desktop Brain drives the physical robot using a lightweight serial/BLE packet protocol:

```json
{
  "state": "SPEAKING",
  "eyes": {
    "expression": "happy",
    "animation": "blink_bounce"
  },
  "servos": {
    "pan": 15,
    "tilt": -10,
    "speed": "smooth"
  },
  "audio_stream": "chunk_or_id"
}
```

### Expressive States:
1. **IDLE / SLEEPING:** Eyes half-closed or breathing animation; head relaxed.
2. **WAKE / LISTENING:** Eyes perk up wide; head tilts up toward the user.
3. **THINKING:** Eyes look toward top corner with a subtle thinking pulse; slight head wobble.
4. **SPEAKING:** Eyes animate in sync with audio amplitude; head nods rhythmically.
5. **ACTION SUCCESS:** Happy squinty arc eyes (`^_^`); joyful double nod.
6. **CONFUSED / ERROR:** Asymmetrical eyes (`O_o`); quizzical head tilt.

---

## 5. Software Stack Breakdown

### Layer 1: Embedded Firmware (`firmware/`)
* **Environment:** Arduino IDE / PlatformIO (C++).
* **Firmware Duties:**
  * Runs OLED eye animation engine (smooth 60fps eye graphics).
  * Smooth servo interpolation (no jittery abrupt motor movements).
  * Streams raw mic audio to Desktop over Bluetooth/Wi-Fi.
  * Receives expression commands and audio playback streams from Desktop.

### Layer 2: Desktop Base Station (`core/`)
* **Transport Driver:** Bluetooth (BLE / RFCOMM via Python `bleak` / `pybluez`) and local WebSocket server.
* **Expression & Motion Engine:** Translates LLM semantic tone into physical servo curves and eye states.
* **Local Brain:** `llama-cpp-python` (100% offline GGUF model).
* **Local Voice:** `faster-whisper` + `Piper TTS`.
* **Cross-Device Controller:** Orchestrates laptop and phone over local mesh.

### Layer 3: Interactive Visual Dashboard (`dashboard/`)
* Displays a digital twin of the cute robot, connected device statuses, music player, and calendar.
