"""Stage 11 Verification Suite: Real-Time WebSocket Event Stream & Voice Console."""

from __future__ import annotations

from http.server import HTTPServer
import json
import threading
import unittest
import urllib.request

from core.mesh.transport import LANWebSocketClient, MeshEnvelope
from dashboard.realtime_ws import DashboardRealtimeHub
from dashboard.server import DeskbotRequestHandler


class TestStage11RealtimeWebSocketAndVoiceConsole(unittest.IsolatedAsyncioTestCase):
    async def test_full_duplex_websocket_chat_voice_and_quick_actions(self) -> None:
        hub = DashboardRealtimeHub(host="127.0.0.1", port=0)
        bound_port = await hub.start()
        client = LANWebSocketClient(host="127.0.0.1", port=bound_port)

        try:
            # 1. Voice transcript query over WebSocket
            voice_env = MeshEnvelope(
                source_device="browser_ws",
                target_device="desktop_host",
                action="voice.transcript",
                payload={"transcript": "check my phone battery"},
            )
            voice_ack = await client.send_envelope(voice_env)
            voice_res = voice_ack.payload
            self.assertEqual(voice_res["event"], "chat.response")
            self.assertTrue(voice_res["voice"])
            self.assertEqual(voice_res["intent"], "phone_check")
            self.assertIn("telemetry", voice_res)

            # 2. Live servo pose update over WebSocket
            pose_env = MeshEnvelope(
                source_device="browser_ws",
                target_device="desktop_host",
                action="robot.set_pose",
                payload={"expression": "listening", "pan": 115, "tilt": 105},
            )
            pose_ack = await client.send_envelope(pose_env)
            self.assertEqual(pose_ack.payload["telemetry"]["pan_deg"], 115)
            self.assertEqual(pose_ack.payload["telemetry"]["expression"], "listening")

            # 3. Quick actions: test_emotions, center_robot, ping_devices
            emo_ack = await client.send_envelope(
                MeshEnvelope(
                    source_device="browser_ws",
                    target_device="desktop_host",
                    action="quick.action",
                    payload={"trigger": "test_emotions"},
                )
            )
            self.assertEqual(
                emo_ack.payload["sequence"],
                ["happy", "listening", "thinking", "confused", "idle"],
            )

            ping_ack = await client.send_envelope(
                MeshEnvelope(
                    source_device="browser_ws",
                    target_device="desktop_host",
                    action="quick.action",
                    payload={"trigger": "ping_devices"},
                )
            )
            self.assertGreaterEqual(len(ping_ack.payload["devices"]), 4)
            self.assertGreaterEqual(len(hub.stream_log), 4)
        finally:
            await client.close()
            await hub.stop()


class TestStage11HTTPAndDOM(unittest.TestCase):
    def setUp(self) -> None:
        self.httpd = HTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2.0)

    def test_dom_voice_toggle_and_quick_action_endpoints(self) -> None:
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/index.html", timeout=2.0) as resp:
            html = resp.read().decode("utf-8")

        for token in (
            'id="btnVoiceDictation"',
            'id="liveEventStream"',
            'id="wsStatusBadge"',
            "toggleVoiceInput()",
            "connectWebSocket(",
            "sendQuickCommand('test_emotions')",
            "sendQuickCommand('ping_devices')",
        ):
            self.assertIn(token, html)

        # Trigger quick_action via HTTP
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/quick_action",
            data=json.dumps({"trigger": "ping_devices"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(data["event"], "quick.action")
        self.assertEqual(data["trigger"], "ping_devices")
        self.assertGreaterEqual(len(data["devices"]), 4)


if __name__ == "__main__":
    unittest.main()
