# 🛒 DESKBOT — Complete Hardware Shopping & Sourcing List

This document lists every electronic and mechanical component required to build the cute physical DESKBOT companion robot, complete with specifications, estimated pricing in Indian Rupees (₹ INR), and direct sourcing recommendations.

---

## 1. Electronics & Compute Components

| # | Component | Exact Model / Spec | Purpose in DESKBOT | Approx Price (INR) | Recommended Indian Vendors |
|---|---|---|---|---|---|
| **1** | **Microcontroller** | **Arduino Nano ESP32** OR **ESP32-S3 Mini / ESP32-WROOM-32** (Type-C) | Main robot controller. Built-in Bluetooth BLE & Wi-Fi, drives servos and OLED. | **₹380 – ₹550** | Robu.in, ElectronicsComp, QuartzComponents, Amazon |
| **2** | **Display (Eyes)** | **0.96 inch I2C OLED Display (SSD1306)** (Blue or White) | Renders animated vector eyes (blinking, happy, listening, thinking). 4 pins (VCC, GND, SCL, SDA). | **₹160 – ₹220** | Robu.in, ElectronicsComp |
| **3** | **Actuators (Neck)** | **2x SG90 or MG90S Micro Servos** (MG90S metal gear recommended for durability) | 1x Pan (horizontal head turn) + 1x Tilt (vertical head nod / puppy tilt). | **₹180 – ₹320** (for pair) | Robu.in, Amazon, ElectronicsComp |
| **4** | **Microphone** | **INMP441 I2S Omnidirectional Digital Microphone** | High-fidelity digital voice audio capture for Whisper STT. | **₹140 – ₹190** | Robu.in, ElectronicsComp |
| **5** | **Audio Amplifier** | **MAX98357A I2S Class D Mono Amplifier** (3.2W) | Clean audio DAC to drive the speaker from ESP32 digital I2S. | **₹160 – ₹220** | Robu.in, ElectronicsComp |
| **6** | **Mini Speaker** | **3 Watt 4 Ohm or 8 Ohm Micro Speaker** (28mm or 31mm diameter) | Output robot voice replies and playful chime sound effects. | **₹40 – ₹80** | Robu.in, Local electronics shop |
| **7** | **Decoupling Capacitor** | **100µF – 220µF Electrolytic Capacitor (16V/25V)** | Placed across 5V and GND rail to prevent ESP32 brownout when servos draw peak current. | **₹5 – ₹10** | Any local electronics store |
| **8** | **Hookup Wires** | **Female-to-Female & Male-to-Female Dupont Jumper Wires** (10cm – 20cm) | Wiring breadboard or direct solder joints inside chassis. | **₹60 – ₹90** (pack of 40) | Amazon, Robu.in |
| **9** | **USB-C Cable** | **USB-A to USB-C or USB-C to USB-C Data Cable** (1 meter) | Connects DESKBOT to your Desktop PC for continuous power and optional Serial tether. | **₹120 – ₹180** | Any standard phone cable |

---

## 2. Mechanical & Fasteners

| # | Item | Specification | Purpose | Approx Price (INR) |
|---|---|---|---|---|
| **10** | **3D Printing Filament** | **PLA or PETG** (White / Pastel Blue / Black) ~120 grams | Prints Head, Neck Bracket, Body Torso, and Desk Base. | **₹120 – ₹180** (cost of 120g from 1kg spool) |
| **11** | **Mounting Screws** | **M2 × 6mm and M2 × 8mm Self-Tapping Screws** (Pack of 10) | Securing OLED display, servos, and horn linkages. | **₹30 – ₹50** |
| **12** | **Anti-Slip Rubber Pads** | **4x Self-Adhesive Silicone Bumpons (10mm dia)** | Stuck to base recesses to keep robot stable on your desk during head movement. | **₹30 – ₹50** |

---

## 3. Total Estimated Project Cost

* **Total Electronics Cost:** ~₹1,200 – ₹1,700
* **Total Mechanical & 3D Print Cost:** ~₹180 – ₹250
* **GRAND TOTAL TO BUILD:** **₹1,400 – ₹1,950 (~$17 – $23 USD)**

*(Compare this to commercial desk robots like Vector or EMO that cost ₹25,000 to ₹35,000, while DESKBOT is 100% private, open-source, and has a full desktop AI brain!)*

---

## 4. Complete Wiring Schematic Table

Connect your components to the **ESP32** board as follows:

```
                      ┌───────────────────────────────┐
                      │      ARDUINO NANO ESP32       │
                      │           / ESP32             │
                      └───────────────┬───────────────┘
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
  [ OLED SCREEN ]                [ 2x SERVOS ]                [ I2S MIC & AMP ]
  VCC  ──► 3.3V                  VCC  ──► 5V (USB Rail)       MIC VDD ──► 3.3V
  GND  ──► GND                   GND  ──► GND                 MIC GND ──► GND
  SCL  ──► GPIO 22               Pan  ──► GPIO 18 (PWM)       MIC SD  ──► GPIO 35
  SDA  ──► GPIO 21               Tilt ──► GPIO 19 (PWM)       MIC WS  ──► GPIO 33
                                                              MIC SCK ──► GPIO 32
                                                              AMP DIN ──► GPIO 27
                                                              AMP BCLK──► GPIO 25
                                                              AMP LRC ──► GPIO 26
```

> **CRITICAL TIP:** Always connect the **220µF capacitor** between the **5V and GND** rail near the servos. Micro-servos pull momentary peak current when suddenly moving; the capacitor buffers this current so the ESP32 does not reset.


---

## 5. Arduino Uno (R3 / R4) + HC-05 / HM-10 Bluetooth Wiring Table

If you are building with an **Arduino Uno** instead of an ESP32:
- **OLED Display (I2C SSD1306):** `VCC -> 5V`, `GND -> GND`, `SDA -> A4`, `SCL -> A5`
- **Pan & Tilt SG90 Servos:** `Pan -> Pin D9 (PWM)`, `Tilt -> Pin D10 (PWM)`, `VCC -> 5V (+ 220µF Cap)`, `GND -> GND`
- **Bluetooth Module (HC-05 / HM-10):** `VCC -> 5V`, `GND -> GND`, `BT TX -> Pin D2 (SoftRX)`, `BT RX -> Pin D3 (SoftTX)`
- **Microphone:** Handled automatically by your Laptop / Mobile microphone over the mesh!
