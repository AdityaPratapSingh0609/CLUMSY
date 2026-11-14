"""DESKBOT / J.A.R.V.I.S. Brain & Reasoning Engine (Stages 2, 5, 15 & 18 integrated)."""

import logging
import os
import sys
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.job_engine import UniversalJobEngine
from core.llm_engine import LLMEngine
from core.llm_fusion import JarvisFusionModel
from core.mesh.device_manager import DeviceMeshManager
from core.protocol import Expression, MotorSpeed
from core.robot_bridge import RobotBridge
from core.tool_router import PluginLoader, ShortcutIntentMatcher, ToolRegistry
from core.voice.voice_commander import normalize_voice_transcript

logger = logging.getLogger("Brain")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class AssistantBrain:
    def __init__(
        self,
        robot_bridge: RobotBridge,
        mesh_manager: DeviceMeshManager,
        llm_engine: Optional[Any] = None,
        tool_registry: Optional[ToolRegistry] = None,
        job_engine: Optional[UniversalJobEngine] = None,
    ):
        self.robot = robot_bridge
        self.mesh = mesh_manager
        self.llm = llm_engine or JarvisFusionModel(max_ram_mb=850)
        self.job_engine = job_engine or UniversalJobEngine()
        self.tools = tool_registry or ToolRegistry()
        if not self.tools.list_tools():
            PluginLoader(self.tools).load_all()
        self.shortcuts = ShortcutIntentMatcher()

    def process_query(
        self,
        user_text: str,
        alternatives: Optional[list[str]] = None,
        execute_os: bool = False,
    ) -> Dict[str, Any]:
        normalized_text = normalize_voice_transcript(user_text, alternatives=alternatives)
        logger.info("Brain received query: '%s' (normalized: '%s')", user_text, normalized_text)
        self.robot.set_thinking()

        result = self.llm.generate(normalized_text)
        thought = result["thought"]
        tool_call = result["tool_call"]
        tool_name = tool_call["tool"]
        tool_params = dict(tool_call["params"])
        spoken_response = result["spoken_response"]

        try:
            target_expression = Expression(result["robot_expression"])
        except ValueError:
            target_expression = Expression.HAPPY

        action_executed: Optional[Dict[str, Any]] = None
        job_artifact: Optional[Dict[str, Any]] = None

        if tool_name == "phone_check":
            res = self.mesh.route_command("phone_node", "get_details", {})
            action_executed = {"tool": "phone_check", "result": res}
            spoken_response = (
                f"I checked your phone! Battery is at {res.get('battery')}, and you have "
                f"{res.get('unread_notifications')} unread notifications."
            )
        elif tool_name in ("launch_app", "app_launcher"):
            target = tool_params.get("target", "desktop_host")
            app_name = tool_params.get("app_name", "Notepad")
            plugin_res = (
                self.tools.execute("app_launcher", {"target": target, "app_name": app_name})
                if self.tools.get("app_launcher")
                else {}
            )
            res = self.mesh.route_command(target, "launch_app", {"app_name": app_name})
            action_executed = {"tool": "launch_app", "result": res, "plugin": plugin_res}
            node = self.mesh.get_device(target)
            node_name = node.name if node else target
            spoken_response = f"Launching {app_name} for you on your {node_name}."
        elif tool_name == "interplatform_hub":
            plat = tool_params.get("platform")
            job_artifact = self.job_engine.execute_job(
                normalized_text,
                job_type="interplatform",
                platform=plat,
                execute_os=execute_os,
            )
            action_executed = {
                "tool": "interplatform_hub",
                "platform": job_artifact.get("platform", plat),
                "action": job_artifact.get("action"),
                "url": job_artifact.get("url"),
                "job_id": job_artifact["job_id"],
            }
            if job_artifact.get("spoken_summary"):
                spoken_response = str(job_artifact["spoken_summary"])
        elif tool_name == "job_executor":
            jtype = tool_params.get("job_type")
            lang = tool_params.get("language")
            job_artifact = self.job_engine.execute_job(
                normalized_text,
                job_type=jtype,
                language=lang,
                execute_os=execute_os,
            )
            action_executed = {
                "tool": "job_executor",
                "job_type": job_artifact["job_type"],
                "job_id": job_artifact["job_id"],
                "language": job_artifact.get("language"),
            }
            if job_artifact["job_type"] == "code":
                code_lang = (job_artifact.get("language") or "python").upper()
                spoken_response = (
                    f"Right away, sir. Here is the {code_lang} implementation:\n"
                    f"```{job_artifact.get('language', 'python')}\n{job_artifact.get('content', '').strip()}\n```\n"
                    f"STDOUT: {job_artifact.get('stdout', '')}"
                )
                target_expression = Expression.CODING
            elif job_artifact["job_type"] == "3d_model":
                target_expression = Expression.EXCITED
        elif tool_name == "media_player":
            act = tool_params.get("action", "play")
            plugin_res = (
                self.tools.execute("media_player", {"action": act})
                if self.tools.get("media_player")
                else {"status": "playing" if act == "play" else act}
            )
            job_artifact = self.job_engine.execute_job(user_text, job_type="music")
            action_executed = {"tool": "media_player", "action": act, "result": plugin_res}
        elif tool_name == "system_monitor":
            plugin_res = (
                self.tools.execute("system_monitor", {})
                if self.tools.get("system_monitor")
                else {"status": "ok"}
            )
            action_executed = {"tool": "system_monitor", "result": plugin_res}
        elif tool_name == "robot_gesture":
            action_executed = {"tool": "robot_gesture", "params": tool_params}

        servo = result["robot_servo"]
        self.robot.express(
            target_expression,
            pan=servo["pan"],
            tilt=servo["tilt"],
            speed=MotorSpeed.SMOOTH,
        )

        return {
            "query": user_text,
            "normalized_query": normalized_text,
            "thought": thought,
            "response": spoken_response,
            "action": action_executed,
            "job_artifact": job_artifact,
            "tool_call": tool_call,
            "robot_state": target_expression.value,
            "robot_servo": servo,
            "engine": result["engine"],
            "fusion": result.get("fusion"),
            "inference_time_ms": result["inference_time_ms"],
            "tokens_per_sec": result["tokens_per_sec"],
        }
