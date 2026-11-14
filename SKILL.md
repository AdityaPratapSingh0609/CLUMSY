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

# DESKBOT // CLUMSY-7X Omni Master Skill Index & Workflow (`SKILL.md`)

## 1. Automated Workflow Tools (`scripts/deskbot_dev.py`)

1. **Stage Checker (`check` & `mark`):**
   - `python scripts/deskbot_dev.py check --plan IMPLEMENTATION_PLAN.md`
   - `python scripts/deskbot_dev.py mark --plan IMPLEMENTATION_PLAN.md --stage <N>`
2. **Command Log Guard (`cmdlog` -> `COMMAND_LOG.md`):**
   - Always check `COMMAND_LOG.md` before executing a command:
     `python scripts/deskbot_dev.py cmdlog --project . --action lookup --command "<cmd>"`
   - Record the command and result after execution:
     `python scripts/deskbot_dev.py cmdlog --project . --action record --command "<cmd>" --result "<result>"`
3. **Diff & Bug-Fix Reviewer (`review` -> `CHANGELOG.md`):**
   - Snapshot workspace and append modified/added files to `CHANGELOG.md`:
     `python scripts/deskbot_dev.py review --project . --note "<stage & bug fix summary>"`
4. **GitHub Commit & Push Gate (`commit --approved`):**
   - Commit and push finalized changes to GitHub:
     `python scripts/deskbot_dev.py commit --project . --message "<commit message>" --approved`

---

## 2. All Skills & Capabilities Included Across Stages 1–37

| # | Skill Name | Module / Path | Purpose |
| :--- | :--- | :--- | :--- |
| 1 | `deskbot-dev-manager` | `scripts/deskbot_dev.py`, `SKILL.md` | 37-stage checker, `CHANGELOG.md` diff reviewer, `COMMAND_LOG.md` guard, and GitHub commit manager |
| 2 | `clumsy-7x-omni-brain` | `dashboard/clumsy_brain.js`, `core/llm_fusion.py` | Unified 7-Model Brain (`Qwen-3.5 + Gemma-4 + Llama-4 + Mistral + Ollama + LM Studio + Jan AI`) |
| 3 | `symbolic-math-algebra-engine` | `dashboard/clumsy_brain.js`, `core/llm_engine.py` | `<1ms` arithmetic, compound percentages/roots, linear algebra (`3x + 5 = 20`), spoken numbers, factorials & trig |
| 4 | `multi-lang-code-studio` | `dashboard/clumsy_brain.js`, `core/job_engine.py` | 6-language (`Python`, `Java`, `C++`, `C`, `JS`, `HTML`) code synthesizer across 20+ algorithms + live runner + code debugger |
| 5 | `hybrid-cloud-wikipedia-router` | `dashboard/clumsy_brain.js`, `core/llm_engine.py` | Resilient `openai-fast` cloud inference with 45s rate-limit cooldown guard + intent-gated Wikipedia Live Knowledge Graph |
| 6 | `offline-encyclopedia-writer` | `dashboard/clumsy_brain.js` | 50+ topic offline science/CS/history/daily-life encyclopedia + structured email, story, poem, essay, translation & comparison generators |
| 7 | `precision-voice-hardware-mic` | `core/voice/hardware_mic.py`, `core/voice/voice_commander.py` | Native Windows SAPI hardware mic daemon (`/api/voice/poll`) + Brave Browser fallback + phonetic STT normalizer + iOS/Android Web Speech |
| 8 | `anatomical-eyeball-engine` | `dashboard/eyeballs.js`, `core/bot_interactive.py` | 60 FPS living eyeballs with 14 emotion-reactive chromatic themes, 50s idle auto-sleep, `"Hey Clumsy"` wake-up shake, and heart/sparkle catchlights |
| 9 | `creative-3d-cad-video-studio` | `core/creative_studio.py`, `dashboard/clumsy_brain.js` | Interactive 3D CAD meshes (Skyscraper, Bridge, Drone, Deskbot), Blender `.py`/`.scad` export, 60 FPS AI video canvas, SVG art & PPT decks |
| 10 | `interplatform-app-mesh` | `plugins/interplatform_hub.py`, `core/mesh/transport.py` | Cross-device Bluetooth/WebSocket sync (`ws://0.0.0.0:9121`) + auto-launch for Netflix, Prime Video, Hotstar, YouTube, Spotify, Gmail, Calendar & Notes |
