from http.server import HTTPServer
import json
import threading
import unittest
import urllib.request

from core.mesh.transport import DualTransportRouter, MeshEnvelope
from core.orchestrator import Orchestrator
from dashboard.server import DeskbotRequestHandler, phone_bridge as server_phone_bridge
from satellite_agent.mobile.phone_bridge import PhoneCompanionBridge


class Stage8PhoneBridgeTests(unittest.IsolatedAsyncioTestCase):
    async def test_ble_gatt_and_termux_battery_updates(self):
        bridge = PhoneCompanionBridge(initial_battery=80)
        self.assertEqual(bridge.update_from_ble_gatt_byte(bytes([64])), 64)
        self.assertEqual(bridge.get_battery_info()["battery_level"], 64)

        info = bridge.update_from_termux_json('{"percentage": 92, "status": "CHARGING"}')
        self.assertEqual(info["battery_level"], 92)
        self.assertTrue(info["charging"])

    async def test_ble_envelope_queries_and_urgent_notification_relay(self):
        orch = Orchestrator()
        await orch.start()
        try:
            # Query phone battery over BLE transport router
            env = MeshEnvelope(
                source_device="desktop_host",
                target_device="phone_node",
                action="get_battery",
                transport="bluetooth",
            )
            reply, _ms = await orch.transport_router.send(env)
            self.assertEqual(reply.payload["battery_level"], 87)

            # Push an urgent notification and verify real-time relay to Orchestrator
            await orch.phone_bridge.push_notification(
                app="Security",
                title="Doorbell Motion",
                body="Person detected at front door",
                urgent=True,
            )
            await orch.audio_queue.wait_until_drained()

            self.assertEqual(len(orch.urgent_alerts), 1)
            self.assertEqual(orch.urgent_alerts[0]["title"], "Doorbell Motion")
            self.assertEqual(orch.phone_bridge.get_notifications_info()["unread_count"], 3)
        finally:
            await orch.stop()

    def test_http_phone_battery_and_notifications_endpoints(self):
        httpd = HTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        port = httpd.server_port
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{port}"
            with urllib.request.urlopen(f"{base}/api/mesh/phone/battery") as resp:
                bat_data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("battery_level", bat_data)

            # Post a new notification + updated battery level
            req = urllib.request.Request(
                f"{base}/api/mesh/phone/notifications",
                data=json.dumps(
                    {
                        "battery_level": 73,
                        "app": "Calendar",
                        "title": "Standup",
                        "body": "Starts in 5 min",
                        "urgent": True,
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                post_res = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(post_res["success"])
            self.assertEqual(post_res["battery_level"], 73)

            with urllib.request.urlopen(f"{base}/api/mesh/phone/notifications") as resp:
                notif_data = json.loads(resp.read().decode("utf-8"))
            self.assertGreaterEqual(notif_data["unread_count"], 3)
            self.assertEqual(server_phone_bridge.battery_level, 73)
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()
