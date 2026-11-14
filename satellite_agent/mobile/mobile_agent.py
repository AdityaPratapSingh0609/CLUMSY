"""Mobile Stream-Flow "Deskbot Eyes" & Personal AI Agent (Stage 17 & Stage 19 — Bug Fix #6).

Once the user's smartphone connects to the Laptop Hub (over Wi-Fi LAN or Bluetooth PAN):
  1. Performs an automatic recognition handshake (`connect_laptop_handshake`).
  2. Transforms the phone into the full-screen **Deskbot Living Eyeballs** avatar
     with continuous always-on microphone streaming and J.A.R.V.I.S. speaker output.
  3. Can trigger any job or app on the Laptop Hub (`Java/Python/C++` code, PPT slides,
     SVG graphics, system music, launching desktop apps) and manage mobile notes/alerts.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from core.job_engine import UniversalJobEngine
from core.llm_fusion import JarvisFusionModel
from core.voice.voice_commander import normalize_voice_transcript
from satellite_agent.mobile.phone_bridge import PhoneCompanionBridge


def strip_code_for_speech(text: str) -> str:
    """Strips fenced code blocks from a chat message so TTS speaks only the conversational sentence."""
    if not text:
        return ""
    without_fences = re.sub(r"```[\s\S]*?```", "", text)
    without_stdout = re.sub(r"STDOUT:.*$", "", without_fences, flags=re.MULTILINE)
    cleaned = " ".join(without_stdout.split()).strip()
    return cleaned or "Right away, sir. I have displayed the output on your screen."


class MobilePersonalAgent:
    """Standalone Mobile 'Deskbot Eyes' Stream-Flow App & Personal AI Agent synced to the Laptop Hub."""

    def __init__(
        self,
        phone_bridge: Optional[PhoneCompanionBridge] = None,
        fusion_model: Optional[JarvisFusionModel] = None,
        job_engine: Optional[UniversalJobEngine] = None,
    ) -> None:
        self.phone_bridge = phone_bridge or PhoneCompanionBridge()
        self.fusion_model = fusion_model or JarvisFusionModel()
        self.job_engine = job_engine or UniversalJobEngine()

        self.bt_paired_to_laptop = True
        self.bt_link_type = "Laptop-StreamFlow-Link (Wi-Fi / BT PAN)"
        self.agent_name = "JARVIS Deskbot Eyes (Mobile Stream-Flow Agent)"
        self.connected_device_name = "User-Smartphone"
        self.stream_flow_active = True
        self.always_on_mic = True
        self.voice_output_target = "source_device"  # "source_device", "phone", "laptop", or "both"
        self.current_eye_reaction = "happy"
        self.last_handshake_ts = time.time()

        self.notes: List[Dict[str, Any]] = [
            {"id": "note_1", "text": "Sync Arduino Uno servo calibration", "done": False},
            {"id": "note_2", "text": "Review JARVIS-X1 4-model fusion telemetry", "done": False},
        ]
        self.chat_history: List[Dict[str, Any]] = []

    def connect_laptop_bluetooth(
        self,
        device_name: str = "User-Smartphone-BT",
        always_on_mic: bool = True,
        voice_target: str = "source_device",
    ) -> Dict[str, Any]:
        """Pair/handshake the phone app with the Laptop Hub and activate Full-Screen Deskbot Eyes mode."""
        self.bt_paired_to_laptop = True
        self.connected_device_name = device_name
        self.stream_flow_active = True
        self.always_on_mic = always_on_mic
        self.voice_output_target = voice_target
        self.current_eye_reaction = "happy"
        self.last_handshake_ts = time.time()
        return {
            "status": "connected",
            "bt_paired_to_laptop": self.bt_paired_to_laptop,
            "device_name": self.connected_device_name,
            "bt_link_type": self.bt_link_type,
            "agent_name": self.agent_name,
            "stream_flow_active": self.stream_flow_active,
            "always_on_mic": self.always_on_mic,
            "voice_output_target": self.voice_output_target,
            "eye_reaction": self.current_eye_reaction,
            "battery_level": self.phone_bridge.battery_level,
            "welcome_speech": "Deskbot Eyes linked to your Laptop Hub, sir. Microphone and speakers are online.",
        }

    def ask_agent(
        self,
        query: str,
        source_device: str = "mobile_app",
        alternatives: Optional[List[str]] = None,
        execute_os: bool = False,
    ) -> Dict[str, Any]:
        """Process a continuous stream-flow voice or text command from the Phone Deskbot Eyes app."""
        q = normalize_voice_transcript(query or "", alternatives=alternatives)
        if not q:
            return {"error": "empty_query"}

        # Check if the user is adding a mobile reminder/task
        if q.lower().startswith(("remind me to ", "add note ", "add task ")):
            for prefix in ("remind me to ", "add note ", "add task "):
                if q.lower().startswith(prefix):
                    note_text = q[len(prefix) :].strip()
                    break
            else:
                note_text = q
            item = {"id": f"note_{len(self.notes) + 1}", "text": note_text, "done": False}
            self.notes.append(item)
            reply = f"Saved to your Mobile Agent notes: '{note_text}'."
            spoken_tts = reply
            fusion_res = self.fusion_model.generate(q)
            job_artifact = self.job_engine.execute_job(q, job_type="interplatform", platform="notes")
            reaction = "happy"
        else:
            fusion_res = self.fusion_model.generate(q)
            reply = fusion_res["spoken_response"]
            reaction = fusion_res.get("robot_expression", "happy")
            job_artifact = None
            tool_name = fusion_res["tool_call"]["tool"]
            if tool_name == "interplatform_hub":
                plat = fusion_res["tool_call"]["params"].get("platform")
                job_artifact = self.job_engine.execute_job(
                    q,
                    job_type="interplatform",
                    platform=plat,
                    execute_os=execute_os,
                )
                if job_artifact.get("spoken_summary"):
                    reply = str(job_artifact["spoken_summary"])
                reaction = "happy"
            elif tool_name == "job_executor":
                jtype = fusion_res["tool_call"]["params"].get("job_type")
                lang = fusion_res["tool_call"]["params"].get("language")
                job_artifact = self.job_engine.execute_job(
                    q,
                    job_type=jtype,
                    language=lang,
                    execute_os=execute_os,
                )
                if job_artifact["job_type"] == "code":
                    code_lang = (job_artifact.get("language") or "python").upper()
                    reply = (
                        f"Right away, sir. Here is your {code_lang} program:\n"
                        f"```{job_artifact.get('language', 'python')}\n{job_artifact.get('content', '').strip()}\n```\n"
                        f"STDOUT: {job_artifact.get('stdout', '')}"
                    )
                    reaction = "coding"
                elif job_artifact["job_type"] == "3d_model":
                    reaction = "excited"
            elif tool_name == "media_player":
                job_artifact = self.job_engine.execute_job(q, job_type="music")
                reaction = "excited"

            spoken_tts = strip_code_for_speech(reply)

        self.current_eye_reaction = reaction
        entry = {
            "query": q,
            "response": reply,
            "spoken_tts": spoken_tts,
            "source_device": source_device,
            "voice_output_target": self.voice_output_target,
            "eye_reaction": reaction,
            "robot_servo": fusion_res.get("robot_servo", {"pan": 90, "tilt": 95}),
            "lead_specialist": fusion_res["fusion"]["lead_specialist"],
            "fusion_weights": fusion_res["fusion"]["weights"],
            "job_artifact": job_artifact,
            "timestamp": time.time(),
        }
        self.chat_history.append(entry)
        return entry

    def get_agent_state(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "bt_paired_to_laptop": self.bt_paired_to_laptop,
            "device_name": self.connected_device_name,
            "bt_link_type": self.bt_link_type,
            "stream_flow_active": self.stream_flow_active,
            "always_on_mic": self.always_on_mic,
            "voice_output_target": self.voice_output_target,
            "eye_reaction": self.current_eye_reaction,
            "battery": self.phone_bridge.get_battery_info(),
            "notifications": self.phone_bridge.get_notifications_info(),
            "notes": self.notes,
            "recent_chats": self.chat_history[-10:],
            "fusion_model": self.fusion_model.FUSION_NAME,
        }
