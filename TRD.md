# Technical Requirement Document (TRD)
## Project Name: DESKBOT — Cute Physical Avatar & Local AI Mesh
**Version:** 1.0.0  
**Status:** Active Engineering Specification  
**Target Environment:** Microcontroller (Arduino C++ / ESP-IDF) + Desktop Base (Python 3.10+ / GGUF)

---

## 1. System Engineering Overview

DESKBOT decouples **physical actuation/expression** from **cognitive AI inference**:
* **Physical Edge (Robot Avatar):** Executes low-latency motor control, 60 FPS OLED eye rendering, and raw audio I/O on an **Arduino Nano ESP32 / ESP32-S3**.
* **Base Station (Desktop Host):** Executes local offline Speech-to-Text (STT), Large Language Model reasoning (GGUF SLM), Text-to-Speech (TTS), and multi-device mesh command routing.
* **Interconnect:** Bluetooth (Serial Port Profile SPP / BLE GATT) and Local Wi-Fi (WebSockets).

---

## 2. Hardware Engineering & Circuit Specifications

### 2.1 Microcontroller Unit (MCU) Pinout
| Pin Label | Function | Connected Peripheral | Electrical Specification |
| :--- | :--- | :--- | :--- |
| **GPIO 21** | I2C SDA | SSD1306 0.96" OLED Display | 3.3V Logic, 4.7kΩ internal/external pull-up |
| **GPIO 22** | I2C SCL | SSD1306 0.96" OLED Display | 3.3V Clock (400 kHz Fast Mode) |
| **GPIO 18** | PWM Channel 0 | Pan Servo (SG90 Micro Servo) | 50 Hz PWM, 500µs – 2400µs pulse width |
| **GPIO 19** | PWM Channel 1 | Tilt Servo (SG90 Micro Servo) | 50 Hz PWM, 500µs – 2400µs pulse width |
| **GPIO 32** | I2S BCLK | INMP441 Digital Microphone | Audio Bit Clock (16-bit, 16 kHz) |
| **GPIO 33** | I2S WS / LRC | INMP441 Digital Microphone | Word Select / Left-Right Clock |
| **GPIO 35** | I2S SD / DATA | INMP441 Digital Microphone | Serial Audio Data In |
| **GPIO 25** | I2S BCLK | MAX98357A Audio Amplifier | Speaker Bit Clock |
| **GPIO 26** | I2S LRC | MAX98357A Audio Amplifier | Speaker Word Select |
| **GPIO 27** | I2S DIN | MAX98357A Audio Amplifier | Audio Data Out to Speaker |
| **VIN / 5V** | System Power | USB-C 5V Rail | Regulated 5.0V ± 5%, min 2.0A |
| **GND** | Common Ground | Common Ground Bus | Star-ground topology to eliminate motor noise |

### 2.2 Power Distribution & Decoupling
* **Servo Inrush Suppression:** Servos generate inductive voltage spikes and inrush currents (up to 650mA peak per motor).
* **Decoupling Capacitor:** A **100µF – 220µF low-ESR electrolytic capacitor** must be placed across the 5V and GND rail directly adjacent to the servo power pins to prevent MCU brownout resets.
* **Separate Power Rails:** The MCU 3.3V LDO regulator must NOT supply power to the servos. Servos are powered directly from the 5V USB bus.

---

## 3. Mechanical & 3D Tolerances (`cad/`)

### 3.1 Dimensions & Masses
* **Outer Enclosure:** 68mm (W) × 54mm (H) × 50mm (D) [Head] | 58mm × 44mm × 48mm [Body].
* **Head Assembly Weight:** ~58 grams (including OLED, tilt bracket, and mic).
* **Required Servo Torque:**
  * SG90 stall torque = $1.8\text{ kg}\cdot\text{cm} \approx 0.176\text{ N}\cdot\text{m}$.
  * At a 25mm pivot distance, maximum head load = $0.058\text{ kg} \times 2.5\text{ cm} = 0.145\text{ kg}\cdot\text{cm}$.
  * **Safety Factor:** $\frac{1.8}{0.145} \approx 12.4\times$ (adequate headroom; zero motor strain).

### 3.2 Fabrication Tolerances
* **Snap-Fit / Slide Tolerance:** $0.30\text{ mm}$ radial clearance.
* **Screw Mounts:** M2 self-tapping holes with nominal pilot diameter of $1.75\text{ mm}$.
* **Layer Height:** $0.16\text{ mm} - 0.20\text{ mm}$, Wall Thickness: $\ge 2.4\text{ mm}$ (3 perimeters).

---

## 4. Embedded Firmware Architecture (`firmware/`)

### 4.1 Execution Model
The firmware utilizes an event-driven cooperative loop on Core 1 of the ESP32 (while Core 0 manages the Bluetooth stack):
* **Render Loop:** OLED update at ~60 Hz (16.6ms cycle).
* **Motor Easing Loop:** Servos update every 15ms with step interpolation to prevent mechanical jerk:
  $$\theta_{t} = \theta_{t-1} + \text{sign}(\theta_{\text{target}} - \theta_{t-1}) \cdot \min(|\theta_{\text{target}} - \theta_{t-1}|, \Delta_{\text{step}})$$
* **Bluetooth Ingestion:** Non-blocking ring-buffer with newline termination (`\n`).

### 4.2 OLED Graphic Buffer Management
* **Screen Resolution:** 128 × 64 monochrome OLED (SSD1306).
* **Buffer Size:** $\frac{128 \times 64}{8} = 1024\text{ bytes}$ internal SRAM.
* **Expressions State Machine:**
  * `idle`: Round pupils with catchlight circles; pseudo-random blink trigger every 3500–5000ms.
  * `happy`: Quadratic Bezier arc eyes with inverted masking.
  * `listening`: Enlarged pupils ($r=16\text{px}$) with scaled specular highlights.
  * `thinking`: Offset pupils looking upper-right ($x+4, y-6$).
  * `confused`: Asymmetric pupil diameters ($r_1=16\text{px}, r_2=8\text{px}$).

---

## 5. Desktop Base Station Engine (`core/`)

### 5.1 Local Offline Intelligence Stack
* **LLM Engine:** `llama-cpp-python` (C++ bindings with AVX2/CUDA/Vulkan acceleration).
* **Recommended Models:**
  * `Qwen2.5-1.5B-Instruct-GGUF` (Q4_K_M, ~1.1 GB disk, ~1.6 GB RAM).
  * `Llama-3.2-3B-Instruct-GGUF` (Q4_K_M, ~2.0 GB disk, ~2.6 GB RAM).
* **Prompt Template & Tool-Calling Protocol:**
  System prompts enforce structured JSON output for tool invocation:
  ```json
  {"action": "route_command", "target": "laptop_node", "params": {"app_name": "Spotify"}}
  ```

### 5.2 Speech-to-Text (STT) Pipeline
* **Engine:** `faster-whisper` (CTranslate2).
* **Model:** `tiny.en` or `base.en` (Quantization: `int8`).
* **Audio Input:** 16,000 Hz, 16-bit, mono PCM.
* **Inference Latency:** $\approx 180\text{ ms} - 350\text{ ms}$ on modern x86 CPU.

### 5.3 Text-to-Speech (TTS) Pipeline
* **Engine:** `Piper TTS` (ONNX runtime neural voice).
* **Voice Model:** `en_US-lessac-medium` or `en_US-amy-low`.
* **Real-Time Factor (RTF):** $< 0.15$ (generates 1 second of audio in under 150ms).

---

## 6. Multi-Device Mesh & Network Protocol

### 6.1 Unified Command Packet Spec (JSON over Bluetooth / Socket)
```json
{
  "protocol_version": "1.0",
  "message_id": "uuid4",
  "state": "HAPPY|LISTENING|THINKING|IDLE|CONFUSED",
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
  "sound_fx": "optional_audio_id"
}
```

### 6.2 Mesh Node Routing Matrix
| Node ID | Transport Type | Primary Services Provided | Target Payload Handler |
| :--- | :--- | :--- | :--- |
| `robot_avatar` | Bluetooth RFCOMM / BLE | OLED eyes, pan/tilt servos, microphone, speaker | `core/robot_bridge.py` |
| `phone_node` | Bluetooth BLE GATT | Battery percentage, unread notifications count, SMS alert | `core/mesh/device_manager.py` |
| `laptop_node` | WebSocket (Port 9120) | Native application execution, media keys, system state | `satellite_agent/pc_client.py` |
| `desktop_host` | Local IPC | Base orchestrator, GGUF brain, STT, TTS, Dashboard API | `core/orchestrator.py` |

---

## 7. Interactive Dashboard Server (`dashboard/`)

* **HTTP Server:** Python standard library `http.server` (zero pip dependencies required).
* **Endpoints:**
  * `GET /`: Serves `dashboard/index.html`.
  * `GET /api/status`: Returns JSON snapshot of connected mesh nodes and current robot state.
  * `POST /api/query`: Receives `{"query": "string"}` and returns `{"response": "string", "robot_state": "string", "action": {}}`.
* **Port:** Default `8080` (configurable).

---

## 8. Verification & Performance Benchmarks

| Metric | Target Specification | Validation Method |
| :--- | :--- | :--- |
| **Bluetooth Packet Latency** | $< 50\text{ ms}$ round-trip | Measured timestamp from Desktop send to MCU ACK |
| **Servo Jitter** | $0\text{ deg}$ fluctuation at rest | Oscilloscope check on PWM signal; mechanical test |
| **Dashboard Responsiveness** | $60\text{ FPS}$ eye animation render | Chrome DevTools Performance profile |
| **System Idle Memory (Desktop)**| $< 150\text{ MB}$ RAM | Task Manager measurement without GGUF loaded |
| **Speech Processing Latency** | $< 1.5\text{ s}$ total response | End-of-speech to first audio output token |

---

## 9. Security & Failsafes

1. **Servo Boundary Clamps:** Firmware clamps servo pulses strictly between $15^\circ$ and $165^\circ$ to prevent mechanical binding against 3D printed stops.
2. **Bluetooth Connection Watchdog:** If no heartbeat packet is received within $10\text{ seconds}$, the robot smoothly transitions to `sleepy` / `idle` center position ($90^\circ, 90^\circ$).
3. **100% Air-Gapped Operation:** No outbound HTTP/HTTPS requests are initiated. All sockets bind exclusively to `127.0.0.1` and local mesh interfaces.
