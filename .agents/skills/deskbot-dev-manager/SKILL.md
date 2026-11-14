---
name: deskbot-dev-manager
description: >-
  DESKBOT / CLUMSY-7X Omni 37-stage master project development manager and QA
  workflow skill. Use when working on the DESKBOT / CLUMSY offline-first AI
  assistant & living robot companion: check 37-stage progress in
  IMPLEMENTATION_PLAN.md, consult COMMAND_LOG.md before running new commands and
  log executed commands, review/diff the project and log all bug fixes and file
  changes to CHANGELOG.md before and after coding, and commit+push to GitHub
  once the user has finalized changes. Indexes every skill and subsystem across
  Stages 1–37 including CLUMSY-7X Omni 7-Model Fusion, Symbolic Math & Algebra
  Engine, 6-Language Code Synthesizer & Debugger, Intent-Gated Wikipedia +
  Multi-Endpoint Cloud Bridge, Windows/Mobile/Brave Voice & Hardware Mic Engine,
  60-FPS Living Eyeballs, Arduino Uno Bluetooth Avatar, and Gemini/ChatGPT UI.
---

# DESKBOT // CLUMSY-7X Omni Master Development & QA Skill (37-Stage Edition)

## Overview

Single master workflow skill that orchestrates development, bug-hunting, regression verification, changelog auditing, command logging, and GitHub deployment for **DESKBOT // CLUMSY-7X Omni** across **Stages 1–37**.

Enforces the strict engineering loop:
**`check` stage $\rightarrow$ `cmdlog lookup` $\rightarrow$ `review` (snapshot before coding) $\rightarrow$ implement stage & fix bugs $\rightarrow$ run unit/QA tests & `cmdlog record` $\rightarrow$ `mark` stage complete $\rightarrow$ `review` (append diff to `CHANGELOG.md`) $\rightarrow$ (when user finalizes) $\rightarrow$ `commit --approved`**.

## Quick Start

```powershell
$S="C:\Users\adity\.gemini\config\skills\deskbot-dev-manager\scripts\deskbot_dev.py"
$P="c:\Users\adity\OneDrive\Desktop\DESKBOT"

python $S check --plan "$P\IMPLEMENTATION_PLAN.md"
python $S cmdlog --project $P --action lookup --command "python -m unittest discover -s tests -t . -v"
python $S review --project $P --note "Completed Stage N bug fixes"
python $S mark --plan "$P\IMPLEMENTATION_PLAN.md" --stage 31
python $S commit --project $P --message "Complete Stages 31-37 (60-Bug ChatGPT Parity Overhaul)" --approved
```

## Complete Skill & Subsystem Index (Stages 1–37)

| Skill / Subsystem | Primary Files | Stage(s) |
| :--- | :--- | :--- |
| **Stage Checker & Plan Tracker** | `scripts/deskbot_dev.py check`, `mark`, `IMPLEMENTATION_PLAN.md` | Stages 1–37 |
| **Diff Reviewer & Changelogger** | `scripts/deskbot_dev.py review`, `CHANGELOG.md`, `.deskbot_state.json` | Stages 1–37 |
| **Command Registry Guard** | `scripts/deskbot_dev.py cmdlog`, `COMMAND_LOG.md` | Stages 1–37 |
| **GitHub Commit & Push Gate** | `scripts/deskbot_dev.py commit --approved` | Stages 1–37 |
| **Async Event Bus & YAML Config** | `core/event_bus.py`, `core/config.py`, `config/config.yaml` | Stage 1 |
| **Offline GGUF LLM Engine** | `core/llm_engine.py`, `models/*.gguf` | Stages 2, 15, 35 |
| **Offline VAD, Wake Word & STT** | `core/voice/vad.py`, `core/voice/wake_word.py`, `core/voice/stt.py` | Stage 3 |
| **Offline Neural TTS & Chimes** | `core/voice/tts.py`, `dashboard/jarvis_hud.js` | Stages 4, 36 |
| **JSON-Schema Tool Router & Plugins** | `core/tool_router.py`, `plugins/app_launcher.py`, `plugins/media_player.py`, `plugins/system_monitor.py` | Stages 5, 21 |
| **Dual-Transport Mesh (BLE + WebSocket)** | `core/mesh/transport.py`, `core/mesh/device_manager.py` | Stage 6 |
| **Laptop Satellite Agent Daemon** | `satellite_agent/pc_client.py`, `scripts/jarvis_background.py` | Stages 7, 20 |
| **Mobile Phone Companion Bridge** | `satellite_agent/mobile/phone_bridge.py`, `satellite_agent/mobile/mobile_agent.py` | Stages 8, 17, 19 |
| **2D/3D Digital Twin & Living Eyeballs** | `dashboard/eyeballs.js`, `dashboard/robot3d.js`, `core/robotics/kinematics.py` | Stages 9, 10, 16, 30 |
| **Full-Duplex WebSocket Hub** | `dashboard/realtime_ws.py`, `dashboard/server.py` | Stages 11, 18, 35 |
| **OpenSCAD 3D Print & Arduino Uno Sim** | `cad/deskbot_model.scad`, `core/robotics/circuit_verifier.py`, `core/robotics/firmware_sim.py`, `firmware/deskbot_avatar.ino` | Stages 12–14 |
| **CLUMSY-7X Omni 7-Model Brain** | `dashboard/clumsy_brain.js`, `core/llm_fusion.py`, `core/brain.py` | Stages 15, 30–35 |
| **Universal Laptop Studio & Job Engine** | `core/job_engine.py`, `core/creative_studio.py`, `plugins/interplatform_hub.py` | Stages 17, 18, 23–29, 34 |
| **Precision Phonetic Voice & Hardware Mic** | `core/voice/voice_commander.py`, `core/voice/hardware_mic.py` | Stages 25, 36 |
| **Symbolic Math, Algebra & Trig Engine** | `dashboard/clumsy_brain.js` (`trySolveMath`), `core/llm_engine.py` (`_try_solve_math`) | Stage 33 |
| **6-Language Code Synthesizer & Debugger** | `dashboard/clumsy_brain.js` (`synthesizeCodeArtifact`), `core/job_engine.py` (`_synthesize_code`) | Stages 17, 34 |
| **Gemini/ChatGPT Streaming UI & Mobile PWA** | `dashboard/index.html`, `dashboard/mobile.html`, `dashboard/sw.js`, `dashboard/manifest.json` | Stages 19, 31, 37 |
