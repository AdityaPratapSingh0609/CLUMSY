"""DESKBOT Mobile Phone Companion Bridge (Stage 8).

Queries and syncs smartphone telemetry over Bluetooth BLE GATT / Termux local
bridge with zero cloud brokers:
- Battery level (BLE Battery Service `0x180F` / characteristic `0x2A19` or
  Termux `termux-battery-status` JSON)
- Unread notifications list and urgent notification relay to the Deskbot
  `EventBus` and `DeviceMeshManager`.
"""

from dataclasses import asdict, dataclass, field
import json
import logging
import time
from typing import Any, Dict, List, Optional

from core.event_bus import EventBus, EventType
from core.mesh.device_manager import DeviceMeshManager
from core.mesh.transport import BluetoothMeshTransport, MeshEnvelope

logger = logging.getLogger("PhoneBridge")

BLE_BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"


@dataclass
class PhoneNotification:
    notification_id: str
    app: str
    title: str
    body: str
    urgent: bool = False
    read: bool = False
    timestamp: float = field(default_factory=time.time)


class PhoneCompanionBridge:
    """
    Maintains real-time phone battery & notification state on the desktop base
    station, exposes a BLE GATT mesh endpoint, and relays urgent alerts to the
    Deskbot `EventBus`.
    """

    def __init__(
        self,
        device_id: str = "phone_node",
        device_name: str = "Mobile Phone",
        initial_battery: int = 87,
        charging: bool = False,
        mesh_manager: Optional[DeviceMeshManager] = None,
        event_bus: Optional[EventBus] = None,
        ble_transport: Optional[BluetoothMeshTransport] = None,
    ):
        self.device_id = device_id
        self.device_name = device_name
        self.battery_level = max(0, min(100, int(initial_battery)))
        self.charging = charging
        self.last_updated = time.time()
        self.mesh = mesh_manager
        self.bus = event_bus
        self._notifications: List[PhoneNotification] = [
            PhoneNotification(
                notification_id="notif_1",
                app="Messages",
                title="Mom",
                body="Call me when you're free",
                urgent=False,
            ),
            PhoneNotification(
                notification_id="notif_2",
                app="GitHub",
                title="PR #42 merged",
                body="DESKBOT mesh transport merged to main",
                urgent=False,
            ),
        ]
        if ble_transport is not None:
            ble_transport.register_gatt_peer(self.device_id, self.handle_ble_envelope)
        self._sync_mesh_node()

    def _sync_mesh_node(self) -> None:
        if self.mesh is not None:
            node = self.mesh.get_device(self.device_id)
            if node is not None:
                node.battery_level = self.battery_level
                node.last_seen = self.last_updated
                node.status = "online"

    def update_from_ble_gatt_byte(self, gatt_payload: bytes) -> int:
        """Parses standard BLE Battery Level characteristic `0x2A19` (uint8 0..100)."""
        if not gatt_payload:
            raise ValueError("Empty BLE battery GATT payload")
        self.battery_level = max(0, min(100, int(gatt_payload[0])))
        self.last_updated = time.time()
        self._sync_mesh_node()
        return self.battery_level

    def update_from_termux_json(self, raw_json: str) -> Dict[str, Any]:
        """Parses output of `termux-battery-status` JSON."""
        data = json.loads(raw_json)
        if "percentage" in data:
            self.battery_level = max(0, min(100, int(data["percentage"])))
        if "status" in data:
            self.charging = str(data["status"]).upper() in ("CHARGING", "FULL")
        self.last_updated = time.time()
        self._sync_mesh_node()
        return self.get_battery_info()

    def get_battery_info(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device": self.device_name,
            "battery_level": self.battery_level,
            "battery": f"{self.battery_level}%",
            "charging": self.charging,
            "status": "online",
            "last_updated": self.last_updated,
        }

    def get_notifications_info(self, unread_only: bool = True) -> Dict[str, Any]:
        items = [n for n in self._notifications if (not unread_only or not n.read)]
        unread_count = sum(1 for n in self._notifications if not n.read)
        return {
            "device_id": self.device_id,
            "device": self.device_name,
            "unread_count": unread_count,
            "notifications": [asdict(n) for n in items],
        }

    def get_details(self) -> Dict[str, Any]:
        unread_count = sum(1 for n in self._notifications if not n.read)
        return {
            "success": True,
            "device_id": self.device_id,
            "device": self.device_name,
            "battery_level": self.battery_level,
            "battery": f"{self.battery_level}%",
            "charging": self.charging,
            "unread_notifications": unread_count,
            "notifications": [asdict(n) for n in self._notifications if not n.read],
            "last_active": "Just now",
        }

    async def push_notification(
        self,
        app: str,
        title: str,
        body: str,
        urgent: bool = False,
        notification_id: Optional[str] = None,
    ) -> PhoneNotification:
        """Records an incoming phone notification and relays urgent alerts to the EventBus."""
        nid = notification_id or f"notif_{len(self._notifications) + 1}"
        notif = PhoneNotification(
            notification_id=nid,
            app=app,
            title=title,
            body=body,
            urgent=urgent,
        )
        self._notifications.append(notif)
        self.last_updated = time.time()
        self._sync_mesh_node()

        if urgent and self.bus is not None:
            await self.bus.emit(
                EventType.MESH_COMMAND_RESULT,
                {
                    "event": "urgent_notification",
                    "device_id": self.device_id,
                    "notification": asdict(notif),
                    "unread_count": sum(1 for n in self._notifications if not n.read),
                },
                source="phone_bridge",
            )
        return notif

    def mark_all_read(self) -> int:
        cleared = 0
        for n in self._notifications:
            if not n.read:
                n.read = True
                cleared += 1
        return cleared

    async def handle_ble_envelope(self, env: MeshEnvelope) -> Dict[str, Any]:
        if env.action == "get_battery":
            return self.get_battery_info()
        if env.action == "get_notifications":
            return self.get_notifications_info(unread_only=bool(env.payload.get("unread_only", True)))
        if env.action == "get_details":
            return self.get_details()
        if env.action == "mark_read":
            return {"success": True, "cleared": self.mark_all_read()}
        return {"success": False, "error": f"Unknown phone action '{env.action}'"}
