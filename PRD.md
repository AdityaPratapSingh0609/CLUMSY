# Product Requirement Document (PRD)
## Project Name: DESKBOT — Cute Physical Avatar & Local AI Mesh

---

## 1. Executive Summary & Product Vision

**DESKBOT** is a 100% free and open-source, fully offline, physical desktop companion robot. It merges a cute, 3D-printed, expressive hardware avatar with a distributed computing mesh powered by your existing desktop computer.

Instead of running sluggish, restricted AI models on low-power microcontrollers or paying for cloud subscriptions, DESKBOT uses an **asymmetric architecture**:
* A tiny **Arduino / ESP32 microcontroller** sits inside a cute 3D-printed desktop robot (approx. 7–9 cm tall), running expressive animated eye emotions on an OLED/LED display and curious head tilts using two micro-servos.
* The robot connects over **Bluetooth (BLE/SPP)** to your **Desktop PC**, treating your computer's RAM, CPU/GPU, and storage as its external brain.
* The system orchestrates tasks across your **phone, laptop, and desktop** (e.g., checking phone battery/notifications, opening apps on your laptop, controlling local music playback, answering questions).
* Note: Calendar/agenda features have been de-scoped in favor of core physical robot interactions and device control.

---

## 2. Core Problems & Solutions

| Problem | DESKBOT Solution |
| :--- | :--- |
| **Privacy & Cloud Lock-in:** Commercial assistants (Alexa, Google, Siri) spy on audio and require internet. | **100% Local & FOSS:** Zero API keys, zero cloud servers, runs completely offline on local GGUF models. |
| **Microcontroller Bottleneck:** Arduino boards cannot run heavy modern LLMs. | **Compute Offloading:** The Arduino only handles motors, screen, and audio I/O; the desktop handles heavy LLM reasoning. |
| **Impersonal AI:** Voice assistants are invisible speakers with no emotion or personality. | **Cute Physical Presence:** 3D-printed mascot with animated eyes (`^_^`, `O_o`) and curious head tilts (OpenSCAD CAD provided). |
| **Fragmented Devices:** Phones, laptops, and PCs operate in separate silos. | **Unified Local Mesh:** DESKBOT bridges phone and laptop actions via unified Bluetooth/LAN protocols. |

---

## 3. System Architecture & Data Flow

```
   [ PHYSICAL ROBOT ]                   [ LOCAL MESH ]                  [ PERIPHERALS ]
 ┌──────────────────────┐           ┌──────────────────────┐          ┌──────────────────┐
 │ • Arduino Nano ESP32 │           │     DESKTOP BASE     │          │   MOBILE PHONE   │
 │ • OLED / LED Eyes    │◄─────────►│  • 100% Offline GGUF │◄────────►│ • Battery status │
 │ • 2-DOF Pan/Tilt     │ Bluetooth │  • Whisper STT       │Bluetooth │ • Notifications  │
 │ • Digital Mic & Amp  │ (BLE/SPP) │  • Piper TTS Engine  │          └──────────────────┘
 └──────────────────────┘           │  • Web Dashboard     │          ┌──────────────────┐
                                    │  • Mesh Orchestrator │◄────────►│   WORK LAPTOP    │
                                    └──────────────────────┘  Wi-Fi   │ • App Launch     │
                                                                      │ • Media Control  │
                                                                      └──────────────────┘
```

---

## 4. Hardware Specifications & Mechanical CAD Design

| Component | Recommended Specification | Purpose |
| :--- | :--- | :--- |
| **Microcontroller** | **Arduino Nano ESP32** or **ESP32-S3 Mini** | Thumb-sized board, built-in Bluetooth 5 + Wi-Fi, native hardware PWM for servos. |
| **Display (Eyes)** | **0.96" or 1.3" I2C OLED (SSD1306)** or **1.28" Round LCD (GC9A01)** | Renders vector eye animations (blinking, happy squint, thinking pulse). |
| **Actuators (Neck)** | **2x SG90 or MG90S Micro Servos** | 2-DOF Pan (horizontal turn) and Tilt (vertical nod / puppy tilt). |
| **Microphone** | **INMP441 I2S Digital Mic** | Clean omnidirectional digital voice capture. |
| **Speaker / Audio** | **MAX98357A I2S DAC + 3W mini speaker (28mm)** | Clear offline voice output and sound effects. |
| **Chassis CAD** | **Parametric OpenSCAD Model (`cad/deskbot_model.scad`)** | 4-part 3D printable assembly (Head, Neck, Torso, Base). |
| **Power** | **USB-C 5V / 2A Input** | Clean power for servos and MCU via desktop USB or wall adapter. |

---

## 5. Software Architecture

### 5.1 Embedded Firmware (`firmware/`)
* **Platform:** Arduino C++ / ESP-IDF.
* **Responsibilities:**
  1. Real-time eye rendering on OLED/LED display at 60 FPS.
  2. Smooth servo interpolation using easing curves (preventing robotic jerky snaps).
  3. Bluetooth Serial / BLE communication with the Desktop Base.
  4. Audio stream pass-through.

### 5.2 Desktop Core Brain (`core/`)
* **Platform:** Python 3.10+ (AsyncIO).
* **Components:**
  1. **Local Brain:** Offline quantized SLM (e.g., *Qwen 2.5 1.5B/3B* or *Llama 3.2 1B/3B*) running via `llama-cpp-python`.
  2. **Speech Pipeline:** `openWakeWord` (wake detection) + `faster-whisper` (STT) + `Piper TTS` (neural voice).
  3. **Emotion Engine:** Maps semantic output (e.g. positive tone, confusion, processing delay) into physical servo angles and eye states.
  4. **Device Mesh Manager:** Discovers, pairs, and relays actions to laptops and phones.

### 5.3 Interactive Dashboard (`dashboard/`)
* **Platform:** HTML5 / CSS3 / Vanilla JS (zero external bloat, served via lightweight Python server).
* **Capabilities:**
  * Real-time Digital Twin rendering of the robot's eyes and servo angles.
  * Live status for Phone (battery, unread notifications) and Laptop.
  * Voice dictation input + text prompt console.
  * Local media player controller.

---

## 6. Functional Requirements (FR)

### FR-1: Expressive Physical Animation
* **FR-1.1:** The robot must support 6 core emotional states: `IDLE`, `LISTENING`, `THINKING`, `SPEAKING`, `HAPPY`, `CONFUSED`.
* **FR-1.2:** In `IDLE` state, the robot must execute natural eye blinks every 3 to 5 seconds and subtle head scanning movements.
* **FR-1.3:** Motor movements must be rate-limited and smoothly interpolated to ensure cute, organic gestures.

### FR-2: 100% Offline Voice & Intelligence
* **FR-2.1:** The system must execute without an active internet connection.
* **FR-2.2:** Intent classification and tool calling must run on local compute.
* **FR-2.3:** Audio transcription and speech synthesis must use offline models (faster-whisper and Piper).

### FR-3: Multi-Device Mesh Control
* **FR-3.1:** **Phone Integration:** The system must read battery percentage and unread notification counts over Bluetooth.
* **FR-3.2:** **Laptop Integration:** The system must trigger native application launches (e.g., Spotify, Browser, VS Code) on the target machine.
* **FR-3.3:** **Local Media:** The system must control local audio playback.

### FR-4: Interactive Dashboard
* **FR-4.1:** The dashboard must be accessible locally at `http://127.0.0.1:8080`.
* **FR-4.2:** Users must be able to trigger expressions manually and test motor positions from the UI.
* **FR-4.3:** The dashboard must provide a responsive chat/voice interaction log.

---

## 7. Non-Functional Requirements (NFR)

* **NFR-1 (Latency):**
  * Motor command response: `< 50 ms` over Bluetooth.
  * Voice processing latency (STT + 1.5B SLM + TTS): `< 1.5 seconds` on modern desktop hardware.
* **NFR-2 (Resource Footprint):**
  * Microcontroller RAM usage: `< 300 KB`.
  * Desktop Background Idle RAM: `< 150 MB` (scales to ~1.5 GB when GGUF model is loaded).
* **NFR-3 (Privacy):** Zero network packets transmitted to any third-party or cloud servers.
* **NFR-4 (Extensibility):** New skills and device actions must be addable via modular Python plugins without rebuilding the core engine.

---

## 8. Communication Protocol Specification

Packet format exchanged over Bluetooth between Desktop and Arduino:

```json
{
  "state": "HAPPY",
  "eyes": {
    "expression": "happy",
    "brightness": 255,
    "auto_blink": true
  },
  "servos": {
    "pan": 90,
    "tilt": 95,
    "speed": "smooth"
  },
  "sound_fx": "chime_up.wav"
}
```

---

## 9. Phased Development Roadmap

1. **Phase 1: Architecture, 3D CAD & Dashboard Simulator [DONE]**
   - Core protocol, robot bridge simulation, mesh router, OpenSCAD CAD model, and web dashboard complete.
2. **Phase 2: Physical Hardware Assembly [UP NEXT]**
   - 3D print robot head, body, and base from `cad/deskbot_model.scad`.
   - Wire Arduino Nano ESP32, OLED screen, and 2 servos.
   - Flash `firmware/deskbot_avatar.ino` and test Bluetooth pairing.
3. **Phase 3: Offline Voice Pipeline**
   - Integrate `faster-whisper` and `Piper TTS` on Desktop.
   - Load local 1B–3B GGUF model for free offline reasoning.
4. **Phase 4: Full Multi-Device Deployment**
   - Deploy background satellite runner on laptop and companion bridge on phone.
