# 🤖 DESKBOT — Cute Physical Avatar & Local AI Mesh

DESKBOT is a **100% open-source, private, local-first personal assistant**. It combines:
1. **A Cute 3D-Printed Desktop Robot Avatar:**
   - Powered by an **ESP32** or **Arduino**.
   - Expressive animated eyes on an OLED/LCD display (blinking, smiling, squinting, thinking).
   - Micro-servo motors for lifelike head tilts, panning, and expressive nods.
   - Microphones and speakers connected via Bluetooth / Serial.
2. **A Distributed Local Memory Mesh:**
   - The small microcontroller does not need to run heavy models.
   - It offloads compute and memory to your **Desktop PC (The Brain)** over **Bluetooth (BLE) or Local Wi-Fi**.
   - Connects to your **phone** (battery, notifications, status) and **laptop** (launch apps, media controls, multitasking).
3. **An Interactive Visual Dashboard:**
   - Real-time digital twin of the cute robot's facial expressions and motor telemetry.
   - Voice assistant input and text console.
   - Connected mesh device monitor.
   - Local offline media player & agenda calendar.

---

## 📂 Project Directory Structure

```
DESKBOT/
├── ARCHITECTURE.md          # Complete hardware & software blueprint
├── README.md                # Getting started and setup guide
├── core/                    # Desktop Host Core Engine
│   ├── protocol.py          # Robot eye & servo command serialization
│   ├── robot_bridge.py      # Bluetooth / USB Serial bridge (with simulation mode)
│   ├── brain.py             # Offline LLM & tool-calling orchestrator
│   └── mesh/
│       └── device_manager.py# Multi-device registry & command routing
├── dashboard/               # Interactive Web Dashboard
│   ├── index.html           # Modern responsive dashboard & digital twin
│   └── server.py            # Local zero-dependency API & web server
└── firmware/                # Embedded Microcontroller Firmware
    └── deskbot_avatar.ino   # Arduino / ESP32 code for OLED eyes & servos
```

---

## ⚡ Quick Start (Running the Dashboard & Core Now)

You don't need the physical hardware plugged in yet to test! The software includes an automatic **Hardware Simulation Mode**.

### 1. Launch the Dashboard Server
Open a terminal in the project directory and run:
```bash
python dashboard/server.py
```

### 2. Open the Dashboard in your Browser
Navigate to:
```
http://127.0.0.1:8080
```
* **Interact with the Robot Face:** Click the expression buttons (Happy, Think, Listen, Confused, Blink) or watch it automatically idle-blink.
* **Try Voice / Text Commands:**
  * *"Hey Deskbot, check my phone details"*
  * *"Open Spotify on my laptop"*
  * *"Play some music"*
  * *"Can you set up a calendar reminder?"*

---

## 🛠️ Building the Physical Robot (Hardware Guide)

### Bill of Materials (BOM):
* **Microcontroller:** ESP32-WROOM, ESP32-S3, or Arduino Nano ESP32 (~$4)
* **Screen:** 0.96" or 1.3" I2C OLED (SSD1306, 128x64) (~$2)
* **Motors:** 2x SG90 or MG90S Micro Servos (Pan & Tilt) (~$3)
* **Audio:** INMP441 I2S Digital Mic + MAX98357A I2S DAC Amp + 3W mini speaker (~$4)

### Wiring Diagram (ESP32):
| Component | ESP32 Pin | Note |
| :--- | :--- | :--- |
| **OLED SDA** | GPIO 21 | I2C Data |
| **OLED SCL** | GPIO 22 | I2C Clock |
| **Pan Servo Signal** | GPIO 18 | Horizontal panning |
| **Tilt Servo Signal** | GPIO 19 | Vertical head tilt |
| **Power (VCC / GND)** | 5V / GND | Provide clean 5V to servos |

### Flashing the Microcontroller:
1. Open [`firmware/deskbot_avatar.ino`](file:///c:/Users/adity/OneDrive/Desktop/DESKBOT/firmware/deskbot_avatar.ino) in the **Arduino IDE**.
2. Install libraries: `Adafruit SSD1306`, `Adafruit GFX`, `ESP32Servo`, `ArduinoJson`.
3. Select your ESP32 board and click **Upload**.
4. Once flashed, pair your PC to **"Deskbot-Companion"** over Bluetooth.

---

## 🔒 100% Offline & Open-Source Guarantee
* **Zero API keys required.**
* **Zero cloud telemetry or subscriptions.**
* All data remains strictly inside your local home mesh.
