# 🗺️ DESKBOT / J.A.R.V.I.S. — 20-Stage Master Implementation Plan

This document establishes the comprehensive, end-to-end execution roadmap for **DESKBOT (J.A.R.V.I.S. Fusion Edition)**, divided into **20 clear, chronological, and measurable stages**:
* **Stages 1 – 8 (8 Stages):** Backend Server Setup, Offline AI Brain & Multi-Device Mesh
* **Stages 9 – 11 (3 Stages):** Frontend Interactive Interface, Digital Twin & WebSockets
* **Stages 12 – 14 (3 Stages):** 3D Printing, **Arduino Uno** Circuit Verification & Cubic-Easing Firmware (with 100% Virtual Hardware Simulation while physical bot is not yet assembled)
* **Stages 15 – 20 (6 Stages):** **J.A.R.V.I.S. Fusion Upgrade** — Ultra-Low-RAM 4-Model Fusion (`Qwen 3.5 + Gemma 4 + Llama 4 + Mistral`), Bot Bluetooth + Live Mic Activity, Mobile Bluetooth AI Personal Agent, Laptop Universal ASAP Job Engine (`Code + PPT + Graphics + System Media`), Holographic Reactive J.A.R.V.I.S. HUD, and Production Deployment.

---

## 🏗️ PART 1: Backend Infrastructure & Core Brain (Stages 1 – 8)

### Stage 1: Environment & Async Micro-Kernel Foundation ✅
* **Objective:** Establish the Python 3.10+ virtual environment and zero-dependency async event loop.
* **Deliverables:**
  * Project directory structure verification and `.gitignore`.
  * Core `EventBus` pub/sub queue supporting concurrent non-blocking tasks.
  * Configuration loader (`config.yaml`) for device ports, model paths, and user preferences.
* **Success Criteria:** Event bus handles 10,000 internal simulated events/sec without blocking.

### Stage 2: 100% Offline Local SLM / LLM Engine (GGUF Runtime) ✅
* **Objective:** Deploy local language model inference via C++ bindings with zero cloud dependency.
* **Deliverables:**
  * `llama-cpp-python` setup with hardware acceleration (AVX2 for CPU or CUDA/Vulkan for GPU).
  * Integration of quantized **Qwen 2.5 1.5B/3B** or **Llama 3.2 1B/3B** (GGUF Q4_K_M).
  * System prompt engineering for deterministic JSON function calling.
* **Success Criteria:** Model generates tokens locally at $\ge 25\text{ tokens/sec}$ on CPU, consuming $< 2.2\text{ GB}$ of RAM.

### Stage 3: Offline Speech-to-Text (STT) & Wake Word Pipeline ✅
* **Objective:** Real-time offline voice transcription and hands-free activation.
* **Deliverables:**
  * `openWakeWord` lightweight background listener for "Hey Deskbot".
  * `faster-whisper` (`tiny.en` or `base.en`, quantized `int8`) transcribing 16 kHz mono audio.
  * Audio ring-buffer and Voice Activity Detection (VAD) using `webrtcvad` / `silero-vad`.
* **Success Criteria:** Voice transcribed into text within $300\text{ ms}$ of speech ending.

### Stage 4: Neural Text-to-Speech (TTS) & Audio Feedback ✅
* **Objective:** Natural-sounding local voice synthesis.
* **Deliverables:**
  * `Piper TTS` ONNX runtime engine.
  * Voice model cache (`en_US-lessac-medium` or `en_US-amy-low`).
  * Non-blocking audio playback worker with queue management and audio chime triggers.
* **Success Criteria:** Real-Time Factor (RTF) $< 0.15$ (1 second of audio synthesized in $< 150\text{ ms}$).

### Stage 5: Semantic Tool-Calling & Dynamic Plugin Router ✅
* **Objective:** Translate conversational intent into actionable commands.
* **Deliverables:**
  * Tool registry with schema validation (JSON Schema).
  * System tools: `media_player` (local music playback), `app_launcher`, `system_monitor`.
  * Fallback regex / keyword intent matcher for instant zero-latency shortcuts.
* **Success Criteria:** Tool arguments validated with $100\%$ accuracy against schemas.

### Stage 6: Dual-Transport Mesh Core (Bluetooth & Local LAN) ✅
* **Objective:** Establish the communication fabric connecting the desktop to external devices.
* **Deliverables:**
  * Bluetooth driver: `bleak` for BLE GATT services and RFCOMM serial client.
  * LAN driver: WebSocket server (`ws://0.0.0.0:9120`) with mDNS auto-discovery.
  * Packet serialization, UUID framing, and automatic reconnect/retry loop.
* **Success Criteria:** End-to-end packet delivery latency $< 30\text{ ms}$ over Bluetooth and $< 10\text{ ms}$ over LAN.

### Stage 7: Laptop Satellite Agent Daemon ✅
* **Objective:** Enable Deskbot to remotely multitask and control a secondary laptop/PC.
* **Deliverables:**
  * Standalone lightweight Python daemon (`satellite_agent/pc_client.py`).
  * Cross-platform application execution (Windows `start`, macOS `open`, Linux `xdg-open`).
  * System volume, media pause/play, and lock screen triggers.
* **Success Criteria:** Laptop launches requested application (e.g. Spotify, VS Code) within $500\text{ ms}$ of Deskbot command.

### Stage 8: Mobile Phone Companion Bridge ✅
* **Objective:** Query mobile phone telemetry without third-party cloud brokers.
* **Deliverables:**
  * Android companion service (via Bluetooth BLE battery service & notification listener, or local Termux bridge).
  * Deskbot API endpoints: `/api/mesh/phone/battery` and `/api/mesh/phone/notifications`.
  * Event relay to Deskbot brain when urgent notifications arrive.
* **Success Criteria:** Phone battery level and unread counts reflected on the desktop base station in real time.

---

## 🎨 PART 2: Frontend Interface & Interactive Dashboard (Stages 9 – 11)

### Stage 9: Responsive Dashboard Core & Digital Twin Layout ✅
* **Objective:** Deliver a zero-bloat, standalone web dashboard accessible from any browser on the local network.
* **Deliverables:**
  * Modern dark-mode UI with modular cards: Robot Face, Device Mesh, Chat Console, Media Controls.
  * 2D vector OLED eye engine simulating blinking, squinting (`^_^`), thinking, and listening states.
  * Responsive viewport matching both desktop monitors and 7" touchscreen mini displays.
* **Success Criteria:** Dashboard loads in $< 100\text{ ms}$ with zero external CDN dependencies.

### Stage 10: Interactive 3D WebGL Robot Viewer & Real-time Telemetry ✅
* **Objective:** Render an interactive 3D digital model of the physical robot synced to motor telemetry.
* **Deliverables:**
  * 3D canvas rendering the exact CAD geometry (Head, Neck, Torso, Base).
  * 360° mouse/touch orbit controls with auto-centering.
  * Real-time Pan ($15^\circ - 165^\circ$) and Tilt ($15^\circ - 165^\circ$) synchronization with simulated/live servo positions.
* **Success Criteria:** Smooth 60 FPS 3D rendering with $< 5\text{ ms}$ posture update lag.

### Stage 11: Real-Time WebSocket Event Stream & Voice Console ✅
* **Objective:** Two-way live streaming between dashboard and backend engine.
* **Deliverables:**
  * Full-duplex WebSocket connection for live telemetry, chat messages, and device states.
  * Web Speech API microphone dictation toggle for browser-based voice testing.
  * Interactive action triggers (re-center motors, test emotions, toggle media, ping devices).
* **Success Criteria:** Live chat updates instantly with zero page refreshing.

---

## 🤖 PART 3: Physical Robotics, Arduino Uno & Virtual Hardware Simulation (Stages 12 – 14)

### Stage 12: 3D Printing & Chassis Post-Processing ✅
* **Objective:** Fabricate and verify the 4 mechanical components of the robot shell.
* **Deliverables:**
  * OpenSCAD model (`cad/deskbot_model.scad`), slicer profile (`cad/slicer_profile.json`), and STL mesh generator (`core/robotics/cad_verifier.py`).
  * Verified $0.3\text{ mm}$ SG90 servo clearances and base stability.
* **Success Criteria:** All 4 parts pass tolerance checks and export watertight ASCII STL geometry.

### Stage 13: Arduino Uno Circuit, Pinout & Power Budget Verification ✅
* **Objective:** Support **Arduino Uno (R3 / R4)** + **ESP32** pinouts, HC-05/HM-10 Bluetooth wiring, and 220µF servo decoupling, with a built-in circuit/schematic verifier so everything is validated before physical assembly.
* **Deliverables:**
  * Arduino Uno pin mapping: I2C OLED (`A4` SDA, `A5` SCL), Pan Servo (`D9` PWM), Tilt Servo (`D10` PWM), HC-05/HM-10 Bluetooth (`D2` RX, `D3` TX), and 220µF electrolytic decoupling across `5V`/`GND`.
  * Automated circuit, pinout conflict, and power-rail drop verifier (`core/robotics/circuit_verifier.py`).
* **Success Criteria:** Zero pin conflicts, verified 5.0V servo rail stability, and complete Arduino Uno + ESP32 wiring table in `HARDWARE_LIST.md`.

### Stage 14: Arduino Uno Embedded Firmware & Virtual Motion Simulator ✅
* **Objective:** Upgrade `firmware/deskbot_avatar.ino` for **Arduino Uno** (2 KB SRAM safe) & ESP32 with non-linear cubic easing, $15^\circ-165^\circ$ gear clamps, and a full Python Virtual Firmware Simulator (`core/robotics/firmware_sim.py`) so the bot works 100% virtually while hardware is not yet built.
* **Deliverables:**
  * Dual-architecture `firmware/deskbot_avatar.ino` (`#ifdef ARDUINO_AVR_UNO` / ESP32) supporting compact serial/Bluetooth frames (`<P90,T95,E1>`) and JSON packets (`{"state":"HAPPY",...}`).
  * Cubic easing interpolation (`easeInOutCubic`), $15^\circ-165^\circ$ hardware limiters, and 10s Bluetooth watchdog timer.
  * Virtual Arduino Uno emulator (`core/robotics/firmware_sim.py`) responding in $< 5\text{ ms}$.
* **Success Criteria:** Virtual & firmware parser responds to Bluetooth/Serial packets in $< 50\text{ ms}$ with smooth cubic easing and strict $[15^\circ, 165^\circ]$ clamping.

---

## ⚡ PART 4: Bug-Fix Overhaul, Real Local LLM, Dynamic Eyeballs, Phone Stream-Flow Eyes App & Universal J.A.R.V.I.S. Hub (Stages 15 – 22)

### Stage 15: [BUG FIX #1, #2, #3] Real Local GGUF LLM Runtime (`llama-cpp-python` + Model Weights) & Zero-Brag J.A.R.V.I.S. Conversational Brain ✅
* **Fixes:**
  * Fixes **Bug #3** (no local LLM installed — auto-installs `llama-cpp-python` and downloads quantized GGUF weights into `models/`).
  * Fixes **Bug #2** (removes all robotic brag lines like `"At once. Qwen 3.5 and Mistral synthesized..."` so J.A.R.V.I.S. talks naturally and directly answers you).
* **Deliverables:**
  * Standalone `llama-cpp-python` + GGUF model setup in `models/` with multi-turn conversational memory.
  * Upgraded `core/llm_fusion.py` (`Qwen + Gemma + Llama + Mistral` routing) that converses naturally like Iron Man's J.A.R.V.I.S. on any topic.
* **Success Criteria:** Real local model inference runs in Python with `< 850 MB` RAM and natural, direct J.A.R.V.I.S. replies.

### Stage 16: [BUG FIX #4] Ultra-Dynamic Eyeball Engine (Irises, Dilating Pupils, Catchlights, Eyelids, Saccades & 12+ Reactions) ✅
* **Fixes:**
  * Fixes **Bug #4** from your eye screenshot (replaces flat cyan half-circles and removes the ugly `<P90,T95,Ehappy>` text from the OLED screen).
* **Deliverables:**
  * `dashboard/eyeballs.js`: Full anatomical animated **Eyeballs** with Sclera, Glowing Iris, Voice/Light-Dilating Pupil, Dual Specular Catchlights, Articulated Upper/Lower Eyelids, and Expressive Eyebrows.
  * Natural micro-saccades (eye darting), cursor/gaze tracking, voice-reactive pupil pulsing while speaking, and **12+ reactions** (`Idle`, `Happy`, `Excited`, `Love`, `Listening`, `Thinking`, `Speaking`, `Coding`, `Wink`, `Surprised`, `Focused`, `Sleepy`, `Confused`).
* **Success Criteria:** Eyes have visible moving eyeballs/irises/pupils in every state (including Happy) at 60 FPS with zero debug text clutter.

### Stage 17: [BUG FIX #1B] Real Multi-Language Code Generator, Compiler & Live Runner (`Java`, `Python`, `C++`, `JS`, `HTML`) ✅
* **Fixes:**
  * Fixes **Bug #1** from your full screenshot where asking `"write a java code to print my name is aditya pratap singh"` returned a fake Python `execute_jarvis_task` dictionary instead of real Java code.
* **Deliverables:**
  * Upgraded code engine in `core/job_engine.py` + `core/llm_fusion.py` that writes **real, prompt-accurate code** in `Java`, `Python`, `C++`, `C`, `JavaScript`, or `HTML`, displays the code block **directly in the chat bubble AND in the Code Studio**, compiles/runs it locally (`javac`/`java`, `python`, `node`), and shows real `STDOUT`.
* **Success Criteria:** Asking `"write a java code to print my name is aditya pratap singh"` outputs valid Java code (`System.out.println("My name is Aditya Pratap Singh");`) and prints `My name is Aditya Pratap Singh` in `STDOUT`.

### Stage 18: [BUG FIX #5] True Full-Duplex WebSocket Auto-Start (`WS: LIVE CONNECTED`) & Real Microphone Audio Stream ✅
* **Fixes:**
  * Fixes **Bug #5** from your screenshot where the top-right badge was stuck on `WS: HTTP Sync` because the WebSocket server wasn't auto-started inside `run_server()`.
* **Deliverables:**
  * Background asyncio thread inside `dashboard/server.py` running `LANWebSocketServer` (`ws://0.0.0.0:9121`) automatically alongside the HTTP server (`0.0.0.0:8080`) with instant auto-reconnect.
  * Browser live microphone `getUserMedia` + `AudioContext` FFT frequency analyzer + continuous Stream-Flow voice recognition (with 1-tap Mute toggle).
* **Success Criteria:** Top-right badge immediately shows **`WS: LIVE CONNECTED`** and the 16-band waveform reacts to your real voice.

### Stage 19: [BUG FIX #6] Installable Phone "Deskbot Eyes" Stream-Flow App (Connect Handshake $\rightarrow$ Full-Screen Living Eyeballs) ✅
* **Fixes:**
  * Fixes **Bug #6** where `/mobile` couldn't connect from a phone (`127.0.0.1` binding) and didn't show the Deskbot Eyes.
* **Deliverables:**
  * Installable Mobile PWA (`/mobile`, `dashboard/manifest.json`, Service Worker) bound to `0.0.0.0:8080`:
    1. **Screen 1 (Connect to Laptop Hub):** Auto-discovers and pairs with your Laptop Hub over Wi-Fi / Bluetooth PAN (with QR code / 1-tap connect on Laptop dashboard).
    2. **Screen 2 (Full-Screen Deskbot Eyes Mode):** Once recognized, transforms your phone into the full-screen animated **Deskbot Eyeballs**, streaming always-on mic input and speaking J.A.R.V.I.S. replies through the phone speaker (or both phone + laptop).
* **Success Criteria:** Opening `/mobile` connects to the Laptop Hub and switches into full-screen living Eyeballs with continuous voice streaming.

### Stage 20: Always-On Background Daemon & Auto-Connect Persistence (Laptop + Phone Background Mode) ✅
* **Objective:** Ensure both the Laptop app and Phone app auto-connect as soon as your laptop is on, and keep listening/responding in the background while you work in other apps.
* **Deliverables:**
  * Screen `WakeLock` + background audio/WebSocket keepalive on the Phone app so the mic/speaker stream stays alive.
  * Laptop background launcher (`scripts/jarvis_background.py`) + device-aware voice routing (plays J.A.R.V.I.S. voice on whichever device you spoke into, with a 1-tap toggle for Both).
* **Success Criteria:** Continuous hands-free voice loop works seamlessly while switching windows or working in the background.

### Stage 21: Universal "Do-Anything" Laptop Action Engine (Open Any App/Website, Play Any System Song, PPT & SVG Graphics) ✅
* **Objective:** Allow J.A.R.V.I.S. (triggered from either your Phone Eyes App or Laptop Hub) to execute any task on your laptop immediately.
* **Deliverables:**
  * **OS & Web Launcher:** Opens any installed application (`Spotify`, `Chrome`, `VS Code`, `Calculator`, `Notepad`, `Explorer`, `Terminal`, `Settings`) or website/YouTube search on your laptop.
  * **System Song & Media Player:** Plays any song you ask for on your laptop system + controls volume/play/pause.
  * **Custom PPT Slide Deck & SVG Graphic Studio:** Builds custom multi-slide presentations and vector graphics for any topic you ask.
* **Success Criteria:** Voice/text commands from Phone or Laptop immediately open apps, play songs, or generate PPT/graphics on the laptop.

### Stage 22: Deep End-to-End Bug Hunt, Stress Verification & Production Sign-Off ✅
* **Objective:** Bug-test the entire system end-to-end across Laptop and Phone views to guarantee zero regressions.
* **Deliverables:**
  * Automated + live browser verification suite (`tests/test_stage15.py` – `tests/test_stage22.py`) testing every bug from your screenshots (Java code prompt, zero brag text, moving eyeballs, `WS: LIVE CONNECTED`, Phone Eyes handshake, and background voice streaming).
* **Success Criteria:** 100% of unit, integration, and live UI bug tests pass with zero errors.

---

## 🌐 PART 5: Interplatform Ecosystem (`Gmail`, `Calendar`, `Notes`, `Netflix`, `Amazon`), 3D Model / Blender / Creative AI Studio & Precision Voice Engine (Stages 23 – 26)

### Stage 23: Interplatform Connectivity Hub (`Gmail`, `Calendar`, `Notes`, `Netflix`, `Amazon`) ✅
* **Objective:** Connect J.A.R.V.I.S. dynamically to Gmail, Google Calendar, Notes, Netflix, and Amazon so it can open those platforms and execute real tasks (composing/searching emails, scheduling calendar events, saving/searching notes, streaming shows on Netflix, and shopping/searching products on Amazon).
* **Deliverables:**
  * `plugins/interplatform_hub.py` handling `gmail`, `calendar`, `notes`, `netflix`, and `amazon` actions with deep-link URL generation, local ledger persistence (`workspace_output/interplatform/`), live studio preview cards, and optional OS browser launching.
* **Success Criteria:** Voice/text commands dynamically open and perform tasks across Gmail, Calendar, Notes, Netflix, and Amazon.

### Stage 24: 3D Model Rendering, Blender Bridge & Creative AI Studio (`3D Model Maker`, `Blender`, `Video Maker`, `Pic & Graphic Creator`, `Extra AI Tools`) ✅
* **Objective:** Add 3D model creation & interactive 3D rendering, Blender (`bpy`) automation & `.obj`/`.scad` mesh export, AI Video Maker (animated HTML5/Canvas multi-scene video & storyboard), AI Pic/Poster Creator, and extra AI power tools (AI Mind-Map, AI Flowchart, AI Data Chart, AI Summarizer/Translator).
* **Deliverables:**
  * `core/creative_studio.py` integrated into `core/job_engine.py` and `core/brain.py`.
  * Interactive 3D wireframe/shaded model viewer canvas + downloadable `.obj` / `.scad` / `_blender.py` scripts, playable animated video preview, high-res procedural AI pic/graphic canvas, and AI Mind-Map/Flowchart studio.
* **Success Criteria:** Asking to create a 3D model, Blender scene, video, picture/graphic, or AI flowchart generates the artifact in `< 50 ms` and renders an interactive preview in the Studio.

### Stage 25: Precision Voice Recognition & Phonetic Voice Command Normalizer ("Everything Via Voice") ✅
* **Objective:** Make voice recognition rock-solid so every interplatform action, 3D model render, Blender task, video maker, pic creator, and coding job can be triggered 100% hands-free via voice.
* **Deliverables:**
  * `core/voice/voice_commander.py`: Phonetic & fuzzy STT correction (`jeemail` $\rightarrow$ `gmail`, `callender` $\rightarrow$ `calendar`, `net flicks` $\rightarrow$ `netflix`, `blander` $\rightarrow$ `blender`, `three d` $\rightarrow$ `3d`, multi-alternative ranking) + natural voice command parser.
  * Browser real-time interim voice transcript HUD + multi-alternative `SpeechRecognition` (`maxAlternatives = 3`) in `dashboard/index.html` and `dashboard/mobile.html`.
* **Success Criteria:** Misspelled or noisy voice transcripts are normalized with 100% accuracy and trigger the exact target platform or creative AI studio tool.

### Stage 26: Unified Holographic AI Dock & 26-Stage End-to-End Verification ✅
* **Objective:** Add an interactive Interplatform & Creative AI Studio Dock to the Laptop Hub and Mobile App, and verify all 26 stages end-to-end.
* **Deliverables:**
  * Upgraded `dashboard/index.html`, `dashboard/mobile.html`, and `dashboard/server.py` with `/api/interplatform` and `/api/creative` endpoints + 1-tap & voice dock buttons.
  * Comprehensive `tests/test_stage23_to_26.py` suite verifying Stages 23 – 26.
* **Success Criteria:** All 26 stages pass 100% of unit and integration tests.

---

## 🚀 PART 6: Siri-to-Laptop Auto-Launch Streaming, Universal Multi-Part 3D CAD/Blender Engineering Engine, Photorealistic Multi-AI Image Synthesis, Billion-Parameter Token Scale & Emotion-Matched Chromatic Eyeballs (Stages 27 – 30)

### Stage 27: Siri-to-Laptop Cross-Device Auto-Launch Streaming (`Netflix`, `Amazon Prime Video`, `Disney+ Hotstar`, `YouTube`, `Spotify`, `Gmail`, `Calendar`) ✅
* **Objective:** When you speak to the Phone/Board (`"Hey bot, play Stranger Things on Netflix"` or `"Play The Boys on Amazon Prime"`), J.A.R.V.I.S. automatically launches and opens that show directly on the connected **Laptop's native browser/OS** (and broadcasts a live WebSocket `laptop.open_url` event to the Laptop Hub) — no manual `"Launch Now"` click required!

### Stage 28: Universal Procedural 3D Engineering, Architecture & Multi-Component CAD/Blender Generator ✅
* **Objective:** Replace the simple 15-vertex box wireframe from Screenshot 2 with a **True Multi-Component 3D Engineering & Architectural Mesh Generator** capable of generating complex, high-polygon 3D models (`200 – 1,200+` vertices & faces with shaded + wireframe + blueprint views, layer toggles, and multi-object `.obj`/`.scad`/`_blender.py` exports) for **any** subject you ask:
  * **Engineering & Architecture:** Skyscraper / Multi-Story Building with structural columns, floors, truss roof, and heli-pad; Suspension Bridge; Modern Villa / House; Industrial Factory.
  * **Mechanical & Aerospace:** V8 Engine / Turbine Assembly; Quadcopter Drone with 4 rotors; Sports Car / Rover Chassis; Space Rocket / Satellite; Robotic Arm / Mech.
  * **Deskbot & Stark Tech:** Full Articulated Deskbot Assembly (Base + Servo Neck + Head + Dual Eyeballs + Ear Pods + Antenna) and Multi-Ring Arc Reactor.

### Stage 29: Photorealistic Multi-AI Image & Graphic Synthesis Engine (`FLUX.1` / `SDXL` / `Imagen 3` + 2D Ray-Traced Canvas Renderer) ✅
* **Objective:** Replace the flat 3-triangle SVG from Screenshot 3 (`"SUNSET ON GOA BEACH"`) with a **Photorealistic Multi-AI Image Generator** that:
  1. Integrates multi-AI image generation providers (`Pollinations Flux.1-Pro / SDXL`, `HuggingFace Inference API`, `OpenAI DALL-E 3`, `Google Gemini Imagen 3`, `Stability AI`) AND includes a built-in **High-Resolution Pixel/Canvas Ray-Traced Photorealistic Renderer** (rendering realistic ocean waves, specular sun reflections, palm silhouettes, volumetric clouds, neon cityscapes, architectural renders, and portraits directly to PNG/DataURL so it works 100% offline or online!).

### Stage 30: Billion-Parameter Context/Token Scaling & Emotion-Synchronized Chromatic Eyeball Palette ✅
* **Objective:**
  1. Upgrade `core/llm_engine.py` and `core/llm_fusion.py` (`JARVIS-X1-Ultra`) with **Billion-Scale Token Capacity** (`context_length=32768`, `max_tokens=4096`, multi-billion parameter cloud/local hybrid bridge for Qwen 2.5 72B / Gemma 2 27B / Llama 3.3 70B / Mistral Large + unlimited local GGUF token streaming).
  2. Overhaul `dashboard/eyeballs.js` so the **entire eye color scheme (iris, sclera rim, eyebrow neon, lash glow, and background aura)** dynamically shifts to match the exact emotion (`Happy` $\rightarrow$ Warm Golden-Emerald Joy, `Excited` $\rightarrow$ Electric Magenta-Gold Supernova, `Love` $\rightarrow$ Crimson-Rose Pink, `Thinking` $\rightarrow$ Deep Violet-Amber Neural Pulse, `Coding` $\rightarrow$ Matrix Neon Green, `Listening` $\rightarrow$ Emerald Sonar Green, `Confused` $\rightarrow$ Sunset Orange-Purple, `Surprised` $\rightarrow$ Electric Plasma Violet, `Idle` $\rightarrow$ Stark Arc-Reactor Cyan).

