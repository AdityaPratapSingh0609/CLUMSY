"""DESKBOT Multi-Device Mesh Manager (Stages 6–8 integrated).

Tracks, discovers, and routes commands between devices:
- Cute Physical Avatar (`robot_avatar` — Arduino / ESP32)
- Secondary Laptops / PCs (`laptop_node` — via LaptopSatelliteDaemon)
- Smartphone (`phone_node` — via PhoneCompanionBridge)
"""

from dataclasses import asdict, dataclass, field
import logging
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logger = logging.getLogger("DeviceMesh")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@dataclass
class DeviceNode:
    device_id: str
    name: str
    device_type: str        # "robot_avatar", "laptop", "phone", "desktop"
    transport: str          # "bluetooth", "lan_websocket", "local"
    status: str = "online"  # "online", "busy", "offline"
    battery_level: Optional[int] = None
    last_seen: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=list)


class DeviceMeshManager:
    def __init__(self):
        self.devices: Dict[str, DeviceNode] = {}
        self._handlers: Dict[str, Callable[[str, Dict[str, Any]], Dict[str, Any]]] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        self.register_device(
            DeviceNode(
                device_id="desktop_host",
                name="Primary Desktop (Brain)",
                device_type="desktop",
                transport="local",
                capabilities=["llm_brain", "stt", "tts", "orchestrator"],
            )
        )
        self.register_device(
            DeviceNode(
                device_id="robot_avatar",
                name="Cute Deskbot Avatar",
                device_type="robot_avatar",
                transport="bluetooth",
                capabilities=["expressive_eyes", "servo_pan_tilt", "mic_input", "speaker_output"],
            )
        )
        self.register_device(
            DeviceNode(
                device_id="laptop_node",
                name="Work Laptop",
                device_type="laptop",
                transport="lan_websocket",
                capabilities=["app_launch", "volume_control", "media_play", "lock_screen"],
            )
        )
        self.register_device(
            DeviceNode(
                device_id="phone_node",
                name="Mobile Phone",
                device_type="phone",
                transport="bluetooth",
                battery_level=87,
                capabilities=["notifications_read", "battery_status", "sms_read", "alarm_trigger"],
            )
        )

    def register_device(self, node: DeviceNode) -> None:
        self.devices[node.device_id] = node
        logger.info("🔗 Registered mesh node: [%s] '%s' via %s", node.device_id, node.name, node.transport)

    def attach_handler(
        self,
        device_id: str,
        handler: Callable[[str, Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """Attaches a live satellite handler (e.g. LaptopSatelliteDaemon or PhoneCompanionBridge)."""
        self._handlers[device_id] = handler

    def get_device(self, device_id: str) -> Optional[DeviceNode]:
        return self.devices.get(device_id)

    def list_devices(self) -> List[Dict[str, Any]]:
        return [asdict(d) for d in self.devices.values()]

    def route_command(self, target_device_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        node = self.get_device(target_device_id)
        if not node:
            return {"success": False, "error": f"Device '{target_device_id}' not found on mesh."}

        node.last_seen = time.time()
        logger.info("⚡ Routing command to [%s] (%s): action='%s', params=%s", node.name, node.device_id, action, params)

        if target_device_id in self._handlers:
            return self._handlers[target_device_id](action, params)

        if node.device_type == "phone":
            if action == "get_details":
                return {
                    "success": True,
                    "device": node.name,
                    "battery": f"{node.battery_level}%",
                    "unread_notifications": 2,
                    "last_active": "Just now",
                }

        elif node.device_type in ("laptop", "desktop"):
            if action == "launch_app":
                app_name = params.get("app_name", "app")
                return {
                    "success": True,
                    "device": node.name,
                    "message": f"Successfully launched {app_name} on {node.name}",
                }

        return {
            "success": True,
            "device": node.name,
            "action": action,
            "status": "executed",
        }
