"""DESKBOT / J.A.R.V.I.S. Local Dashboard, WebSocket Hub & Mobile Stream-Flow Server (Stages 1–22).

Serves the interactive J.A.R.V.I.S. Laptop Hub (`/`) and Installable Phone
"Deskbot Eyes" Stream-Flow App (`/mobile`), plus REST + full-duplex WebSocket endpoints:
- `GET /api/status`
- `GET /api/handshake`
- `GET /api/fusion/status`
- `GET /api/bot/status`
- `POST /api/bot/bluetooth`
- `POST /api/bot/mic_activity`
- `GET /api/mobile/agent`
- `POST /api/mobile/agent`
- `POST /api/mobile/connect`
- `GET /api/jobs/list`
- `POST /api/jobs/execute`
- `GET /api/ws_info`
- `GET /api/events/recent`
- `GET /api/robot/telemetry`
- `POST /api/robot/telemetry`
- `POST /api/quick_action`
- `POST /api/media`
- `POST /api/query`
- `GET /api/mesh/phone/battery`
- `GET /api/mesh/phone/notifications`
- `POST /api/mesh/phone/notifications`
- `POST /api/mesh/laptop/command`
"""

from __future__ import annotations

import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
import socket
import sys
import threading
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.bot_interactive import BotInteractiveController
from core.brain import AssistantBrain
from core.event_bus import EventBus
from core.job_engine import UniversalJobEngine
from core.llm_fusion import JarvisFusionModel
from core.mesh.device_manager import DeviceMeshManager
from core.mesh.transport import MeshEnvelope
from core.robot_bridge import RobotBridge
from core.voice.voice_commander import normalize_voice_transcript
from dashboard.realtime_ws import DashboardRealtimeHub
from plugins import interplatform_hub, media_player
from satellite_agent.mobile.mobile_agent import MobilePersonalAgent, strip_code_for_speech
from satellite_agent.mobile.phone_bridge import PhoneCompanionBridge
from satellite_agent.pc_client import LaptopSatelliteDaemon
from scripts.jarvis_background import JarvisBackgroundDaemon

logger = logging.getLogger("DashboardServer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def get_local_lan_ip() -> str:
    """Discover the laptop's primary LAN/Wi-Fi IPv4 address for phone pairing."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


# Shared runtime state for the HTTP & WebSocket server
event_bus = EventBus()
robot_bridge = RobotBridge(simulate=True)
robot_bridge.connect()
mesh_manager = DeviceMeshManager()
laptop_daemon = LaptopSatelliteDaemon(node_id="laptop_node", dry_run=True)
phone_bridge = PhoneCompanionBridge(
    device_id="phone_node",
    mesh_manager=mesh_manager,
    event_bus=event_bus,
)
mesh_manager.attach_handler("laptop_node", laptop_daemon.execute_action)
mesh_manager.attach_handler(
    "phone_node",
    lambda action, params: (
        phone_bridge.get_battery_info()
        if action == "get_battery"
        else phone_bridge.get_notifications_info()
        if action == "get_notifications"
        else phone_bridge.get_details()
    ),
)

fusion_model = JarvisFusionModel(max_ram_mb=850)
job_engine = UniversalJobEngine()
bot_controller = BotInteractiveController(
    robot_bridge=robot_bridge,
    event_bus=event_bus,
    board_mode="arduino_uno",
)
mobile_agent = MobilePersonalAgent(
    phone_bridge=phone_bridge,
    fusion_model=fusion_model,
    job_engine=job_engine,
)
bg_daemon = JarvisBackgroundDaemon()
brain = AssistantBrain(
    robot_bridge=robot_bridge,
    mesh_manager=mesh_manager,
    llm_engine=fusion_model,
    job_engine=job_engine,
)
realtime_hub = DashboardRealtimeHub(
    host="0.0.0.0",
    port=0,  # Picks 9121 or an open port automatically when started
    event_bus=event_bus,
    robot_bridge=robot_bridge,
    mesh_manager=mesh_manager,
    phone_bridge=phone_bridge,
    brain=brain,
)

_ws_loop: Optional[asyncio.AbstractEventLoop] = None
_ws_thread: Optional[threading.Thread] = None
_ws_lock = threading.Lock()


def ensure_realtime_ws_started(preferred_port: int = 9121) -> int:
    """Ensure the full-duplex WebSocket server is running on a background thread (Bug Fix #5)."""
    if os.environ.get("VERCEL"):
        return preferred_port
    global _ws_loop, _ws_thread
    with _ws_lock:
        if realtime_hub.port and realtime_hub.port > 0 and _ws_loop is not None:
            return realtime_hub.port

        ready_evt = threading.Event()

        def _runner() -> None:
            global _ws_loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            _ws_loop = loop
            try:
                realtime_hub.ws_server.host = "0.0.0.0"
                realtime_hub.ws_server.port = preferred_port
                loop.run_until_complete(realtime_hub.start())
            except OSError:
                # If preferred_port (9121) is already bound, bind to an ephemeral free port
                realtime_hub.ws_server.port = 0
                loop.run_until_complete(realtime_hub.start())
            ready_evt.set()
            loop.run_forever()

        _ws_thread = threading.Thread(target=_runner, name="JarvisRealtimeWS", daemon=True)
        _ws_thread.start()
        ready_evt.wait(timeout=3.0)
        return realtime_hub.port or preferred_port


def _run_coro_threadsafe(coro: Any) -> Any:
    """Execute an async coroutine safely whether or not the background WS event loop is active."""
    if _ws_loop is not None and _ws_loop.is_running():
        fut = asyncio.run_coroutine_threadsafe(coro, _ws_loop)
        return fut.result(timeout=15.0)
    return asyncio.run(coro)


class DeskbotRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        dashboard_dir = os.path.abspath(os.path.dirname(__file__))
        super().__init__(*args, directory=dashboard_dir, **kwargs)

    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(body)

    def log_message(self, format: str, *args: Any) -> None:
        logger.debug(format, *args)

    _STATIC_MIME_MAP = {
        ".html": "text/html; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".jpg": "image/jpeg",
        ".png": "image/png",
    }

    def _try_serve_static_fast(self, rel_name: str) -> bool:
        dashboard_dir = os.path.abspath(os.path.dirname(__file__))
        target = os.path.join(dashboard_dir, rel_name.lstrip("/"))
        if not os.path.isfile(target):
            return False
        ext = os.path.splitext(target)[1].lower()
        ctype = self._STATIC_MIME_MAP.get(ext, "application/octet-stream")
        with open(target, "rb") as f:
            raw = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
        return True

    def do_GET(self) -> None:
        clean_path = self.path.split("?", 1)[0]
        if clean_path in ("/", "/index.html"):
            if self._try_serve_static_fast("index.html"):
                return
        if clean_path in ("/mobile", "/eyes", "/mobile.html"):
            if self._try_serve_static_fast("mobile.html"):
                return
        if clean_path in ("/manifest.json", "/manifest-desktop.json", "/sw.js", "/eyeballs.js", "/robot3d.js", "/jarvis_hud.js", "/deskbot_render.jpg"):
            if self._try_serve_static_fast(clean_path.lstrip("/")):
                return

        if clean_path == "/api/status":
            ws_port = ensure_realtime_ws_started()
            lan_ip = get_local_lan_ip()
            http_port = self.server.server_address[1] if hasattr(self, "server") else 8080
            self._send_json(
                200,
                {
                    "robot_state": robot_bridge.current_state,
                    "telemetry": robot_bridge.get_telemetry(),
                    "fusion": fusion_model.last_telemetry,
                    "bot": bot_controller.get_status(),
                    "mobile": mobile_agent.get_agent_state(),
                    "devices": mesh_manager.list_devices(),
                    "phone_battery": phone_bridge.battery_level,
                    "phone_unread": phone_bridge.get_notifications_info()["unread_count"],
                    "ws_port": ws_port,
                    "ws_connected": True,
                    "lan_ip": lan_ip,
                    "mobile_url": f"http://{lan_ip}:{http_port}/mobile",
                },
            )
        elif clean_path == "/api/handshake":
            ws_port = ensure_realtime_ws_started()
            lan_ip = get_local_lan_ip()
            http_port = self.server.server_address[1] if hasattr(self, "server") else 8080
            self._send_json(
                200,
                {
                    "status": "laptop_hub_online",
                    "hub_name": "DESKBOT // J.A.R.V.I.S. Master Laptop Hub",
                    "lan_ip": lan_ip,
                    "http_port": http_port,
                    "ws_port": ws_port,
                    "mobile_url": f"http://{lan_ip}:{http_port}/mobile",
                    "stream_flow_ready": True,
                    "always_on_mic": mobile_agent.always_on_mic,
                    "voice_output_target": mobile_agent.voice_output_target,
                    "eye_reaction": bot_controller.current_reaction,
                    "telemetry": robot_bridge.get_telemetry(),
                },
            )
        elif clean_path == "/api/fusion/status":
            self._send_json(200, fusion_model.last_telemetry)
        elif clean_path == "/api/bot/status":
            self._send_json(200, bot_controller.get_status())
        elif clean_path == "/api/mobile/agent":
            self._send_json(200, mobile_agent.get_agent_state())
        elif clean_path == "/api/background/status":
            self._send_json(200, bg_daemon.get_status())
        elif clean_path == "/api/jobs/list":
            self._send_json(200, {"jobs": job_engine.list_jobs()})
        elif clean_path == "/api/ws_info":
            ws_port = ensure_realtime_ws_started()
            lan_ip = get_local_lan_ip()
            self._send_json(
                200,
                {
                    "ws_url": f"ws://127.0.0.1:{ws_port}",
                    "lan_ws_url": f"ws://{lan_ip}:{ws_port}",
                    "ws_port": ws_port,
                    "stream_events": len(realtime_hub.stream_log),
                },
            )
        elif clean_path == "/api/events/recent":
            self._send_json(200, {"events": realtime_hub.stream_log[-25:]})
        elif clean_path == "/api/robot/telemetry":
            self._send_json(200, robot_bridge.get_telemetry())
        elif clean_path == "/api/mesh/phone/battery":
            self._send_json(200, phone_bridge.get_battery_info())
        elif clean_path == "/api/mesh/phone/notifications":
            self._send_json(200, phone_bridge.get_notifications_info())
        else:
            super().do_GET()

    def do_POST(self) -> None:
        clean_path = self.path.split("?", 1)[0]
        try:
            if clean_path == "/api/query":
                data = self._read_json_body()
                source_dev = str(data.get("source_device") or "laptop_hub")
                raw_q = str(data.get("query") or "")
                alts = data.get("alternatives") if isinstance(data.get("alternatives"), list) else None
                norm_q = normalize_voice_transcript(raw_q, alternatives=alts)
                exec_os = bool(data.get("execute_os", False))
                env = MeshEnvelope(
                    source_device=source_dev,
                    target_device="desktop_host",
                    action="voice.transcript" if data.get("voice") else "chat.query",
                    payload={
                        "query": norm_q,
                        "raw_query": raw_q,
                        "voice": bool(data.get("voice", False)),
                        "execute_os": exec_os,
                        "source_device": source_dev,
                    },
                )
                result = _run_coro_threadsafe(realtime_hub.handle_envelope(env))
                result["normalized_query"] = norm_q
                result["spoken_tts"] = strip_code_for_speech(result.get("response", ""))
                result["source_device"] = source_dev
                result["voice_output_target"] = bg_daemon.voice_output_target
                result["speaker_routing"] = bg_daemon.resolve_speaker_targets(source_dev)
                bot_controller.send_bot_pose(
                    pan=result.get("telemetry", {}).get("pan_deg", 90),
                    tilt=result.get("telemetry", {}).get("tilt_deg", 95),
                    expression=result.get("robot_state", "happy"),
                )
                self._send_json(200, result)
            elif clean_path == "/api/jobs/execute":
                data = self._read_json_body()
                prompt = normalize_voice_transcript(str(data.get("prompt") or "JARVIS Job"))
                jtype = data.get("job_type")
                lang = data.get("language")
                plat = data.get("platform")
                exec_os = bool(data.get("execute_os", False))
                artifact = job_engine.execute_job(
                    prompt,
                    job_type=jtype,
                    language=lang,
                    platform=plat,
                    execute_os=exec_os,
                )
                self._send_json(200, artifact)
            elif clean_path == "/api/interplatform":
                data = self._read_json_body()
                prompt = normalize_voice_transcript(str(data.get("prompt") or "Open Gmail"))
                plat = data.get("platform")
                exec_os = bool(data.get("execute_os", False))
                artifact = job_engine.execute_job(
                    prompt,
                    job_type="interplatform",
                    platform=plat,
                    execute_os=exec_os,
                )
                self._send_json(200, artifact)
            elif clean_path == "/api/creative":
                data = self._read_json_body()
                prompt = normalize_voice_transcript(str(data.get("prompt") or "Render a 3D model of Deskbot"))
                jtype = str(data.get("job_type") or "3d_model")
                exec_os = bool(data.get("execute_os", False))
                artifact = job_engine.execute_job(
                    prompt,
                    job_type=jtype,
                    execute_os=exec_os,
                )
                self._send_json(200, artifact)
            elif clean_path == "/api/mobile/connect":
                data = self._read_json_body()
                dev_name = str(data.get("device_name") or "User-Smartphone-Eyes")
                always_on = bool(data.get("always_on_mic", True))
                voice_target = str(data.get("voice_output_target") or "source_device")
                res = mobile_agent.connect_laptop_bluetooth(
                    device_name=dev_name,
                    always_on_mic=always_on,
                    voice_target=voice_target,
                )
                bot_controller.send_bot_pose(pan=90, tilt=96, expression="happy")
                res["ws_port"] = ensure_realtime_ws_started()
                res["lan_ip"] = get_local_lan_ip()
                self._send_json(200, res)
            elif clean_path == "/api/mobile/agent":
                data = self._read_json_body()
                source_dev = str(data.get("source_device") or "mobile_app")
                alts = data.get("alternatives") if isinstance(data.get("alternatives"), list) else None
                exec_os = bool(data.get("execute_os", False))
                res = mobile_agent.ask_agent(
                    str(data.get("query") or ""),
                    source_device=source_dev,
                    alternatives=alts,
                    execute_os=exec_os,
                )
                if "eye_reaction" in res:
                    servo = res.get("robot_servo", {"pan": 90, "tilt": 95})
                    bot_controller.send_bot_pose(
                        pan=servo.get("pan", 90),
                        tilt=servo.get("tilt", 95),
                        expression=res["eye_reaction"],
                    )
                # Broadcast mobile command result + auto_open_url to the connected Laptop Hub over WebSocket!
                job_art = res.get("job_artifact")
                auto_url = (
                    job_art.get("url")
                    if isinstance(job_art, dict) and job_art.get("auto_open_on_laptop")
                    else None
                )
                res["auto_open_url"] = auto_url
                try:
                    _run_coro_threadsafe(
                        realtime_hub.ws_server.broadcast_json(
                            {
                                "action": "mobile.command_sync",
                                "source_device": source_dev,
                                "payload": {
                                    "response": res.get("response"),
                                    "spoken_tts": res.get("spoken_tts"),
                                    "job_artifact": job_art,
                                    "auto_open_url": None,  # already opened natively on the laptop by the server
                                    "telemetry": robot_bridge.get_telemetry(),
                                },
                            }
                        )
                    )
                except Exception:
                    pass
                self._send_json(200, res)
            elif clean_path == "/api/bot/bluetooth":
                data = self._read_json_body()
                mode = str(data.get("mode") or "virtual_bluetooth_uno")
                res = bot_controller.connect_bluetooth(mode=mode, address=data.get("address"))
                self._send_json(200, res)
            elif clean_path == "/api/bot/mic_activity":
                data = self._read_json_body()
                res = bot_controller.process_mic_frame(
                    simulated_text=data.get("text"),
                    rms_override=data.get("rms"),
                )
                self._send_json(200, res)
            elif clean_path == "/api/quick_action":
                data = self._read_json_body()
                env = MeshEnvelope(
                    source_device="dashboard_http",
                    target_device="desktop_host",
                    action="quick.action",
                    payload={"trigger": str(data.get("trigger") or "center_robot")},
                )
                result = _run_coro_threadsafe(realtime_hub.handle_envelope(env))
                self._send_json(200, result)
            elif clean_path == "/api/robot/telemetry":
                data = self._read_json_body()
                expr_str = str(data.get("expression") or robot_bridge.current_expression).lower()
                pan = int(data.get("pan", robot_bridge.current_pan))
                tilt = int(data.get("tilt", robot_bridge.current_tilt))
                pose_out = bot_controller.send_bot_pose(pan=pan, tilt=tilt, expression=expr_str)
                telemetry = robot_bridge.get_telemetry()
                telemetry["eyeballs"] = pose_out["eyeballs"]
                self._send_json(200, telemetry)
            elif clean_path == "/api/media":
                data = self._read_json_body()
                res = media_player.handle_media_player(data)
                self._send_json(200, res)
            elif clean_path == "/api/mesh/phone/notifications":
                data = self._read_json_body()
                if "battery_level" in data:
                    phone_bridge.update_from_ble_gatt_byte(bytes([int(data["battery_level"])]))
                notif = _run_coro_threadsafe(
                    phone_bridge.push_notification(
                        app=str(data.get("app") or "System"),
                        title=str(data.get("title") or "Alert"),
                        body=str(data.get("body") or ""),
                        urgent=bool(data.get("urgent", False)),
                    )
                )
                self._send_json(
                    200,
                    {
                        "success": True,
                        "notification_id": notif.notification_id,
                        "urgent": notif.urgent,
                        "unread_count": phone_bridge.get_notifications_info()["unread_count"],
                        "battery_level": phone_bridge.battery_level,
                    },
                )
            elif clean_path == "/api/mesh/laptop/command":
                data = self._read_json_body()
                action = str(data.get("action") or "launch_app")
                params = data.get("params") or {}
                res = laptop_daemon.execute_action(action, params)
                self._send_json(200, res)
            elif clean_path == "/api/background/config":
                data = self._read_json_body()
                if data.get("heartbeat"):
                    status = bg_daemon.record_heartbeat(str(data.get("device_id") or "phone_eyes_app"))
                else:
                    status = bg_daemon.configure(
                        always_on_mic=data.get("always_on_mic"),
                        voice_output_target=data.get("voice_output_target"),
                        auto_connect_on_boot=data.get("auto_connect_on_boot"),
                    )
                    mobile_agent.voice_output_target = bg_daemon.voice_output_target
                self._send_json(200, status)
            else:
                self._send_json(404, {"error": f"Unknown endpoint {clean_path}"})
        except Exception as exc:
            logger.error("Error handling POST %s: %s", clean_path, exc)
            self._send_json(500, {"error": str(exc)})


def run_server(port: int = 8080, host: str = "0.0.0.0") -> None:
    ws_port = ensure_realtime_ws_started(9121)
    lan_ip = get_local_lan_ip()
    httpd = ThreadingHTTPServer((host, port), DeskbotRequestHandler)
    logger.info("🚀 DESKBOT // J.A.R.V.I.S. Laptop Hub running at http://127.0.0.1:%d", port)
    logger.info("📱 Phone 'Deskbot Eyes' Stream-Flow App URL: http://%s:%d/mobile", lan_ip, port)
    logger.info("⚡ Full-Duplex WebSocket Server active on ws://%s:%d", lan_ip, ws_port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
