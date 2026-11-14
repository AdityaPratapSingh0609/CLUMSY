"""Stage 18 Verification Suite: True Full-Duplex WebSocket Auto-Start (`WS: LIVE CONNECTED`) & Continuous Stream-Flow Mic."""

from __future__ import annotations

import asyncio
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest
import urllib.request

from core.mesh.transport import LANWebSocketClient, MeshEnvelope
from dashboard.server import DeskbotRequestHandler, ensure_realtime_ws_started


class TestStage18WebSocketAutoStartAndStreamMic(unittest.TestCase):
    def setUp(self) -> None:
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2.0)

    def test_01_ws_server_auto_starts_and_accepts_full_duplex_envelopes(self) -> None:
        """Verify Bug Fix #5: /api/status automatically starts the WebSocket server and returns a live ws_port."""
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/status", timeout=3.0) as resp:
            status = json.loads(resp.read().decode("utf-8"))

        self.assertTrue(status["ws_connected"])
        ws_port = int(status["ws_port"])
        self.assertGreater(ws_port, 0)

        # Connect a real WebSocket client to the auto-started ws_port and send a query
        async def _ws_roundtrip() -> dict:
            client = LANWebSocketClient(host="127.0.0.1", port=ws_port)
            await client.connect()
            try:
                env = MeshEnvelope(
                    source_device="test_ws_client",
                    target_device="desktop_host",
                    action="chat.query",
                    payload={"query": "write a java code to print my name is aditya pratap singh"},
                )
                return await client.send_envelope(env)
            finally:
                await client.close()

        reply = asyncio.run(_ws_roundtrip())
        self.assertEqual(reply.payload["event"], "chat.response")
        self.assertIn("My name is Aditya Pratap Singh", reply.payload["response"])

    def test_02_dashboard_has_ws_live_connected_and_continuous_stream_flow_mic(self) -> None:
        html = Path("dashboard/index.html").read_text(encoding="utf-8")
        self.assertIn("WS: LIVE CONNECTED", html)
        self.assertIn("startLiveMicAnalyzer", html)
        self.assertIn("activeRecognition.continuous = true", html)
        self.assertIn("speakJarvisReply", html)


if __name__ == "__main__":
    unittest.main()
