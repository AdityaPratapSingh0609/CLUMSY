"""Stage 19 Verification Suite: Installable Phone 'Deskbot Eyes' Stream-Flow App (Connect Handshake -> Full-Screen Living Eyeballs)."""

from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest
import urllib.request

from dashboard.server import DeskbotRequestHandler


class TestStage19PhoneDeskbotEyesStreamFlowApp(unittest.TestCase):
    def setUp(self) -> None:
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2.0)

    def test_01_pwa_manifest_and_service_worker_served(self) -> None:
        """Verify Bug Fix #6: /manifest.json and /sw.js are served for phone home-screen installation."""
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/manifest.json", timeout=2.0) as resp:
            manifest = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(manifest["start_url"], "/mobile")

        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/sw.js", timeout=2.0) as resp:
            sw_js = resp.read().decode("utf-8")
        self.assertIn("deskbot-eyes", sw_js)

    def test_02_laptop_handshake_and_mobile_eyes_connection_flow(self) -> None:
        """Verify Step 1 (Laptop Handshake) -> Step 2 (Full-Screen Living Eyeballs + Voice Command)."""
        # 1. Probe Laptop Hub handshake
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/handshake", timeout=2.0) as resp:
            hs = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(hs["status"], "laptop_hub_online")
        self.assertTrue(hs["stream_flow_ready"])

        # 2. Complete Phone -> Laptop pairing handshake
        req_conn = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/mobile/connect",
            data=json.dumps({"device_name": "Aditya-Phone-Eyes", "always_on_mic": True}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_conn, timeout=2.0) as resp:
            conn_res = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(conn_res["status"], "connected")
        self.assertTrue(conn_res["stream_flow_active"])
        self.assertTrue(conn_res["always_on_mic"])

        # 3. Speak a command into the Phone Eyes App -> executes on Laptop & returns spoken_tts + eye_reaction
        req_cmd = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/mobile/agent",
            data=json.dumps(
                {
                    "query": "write a java code to print my name is aditya pratap singh",
                    "source_device": "mobile_app",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_cmd, timeout=3.0) as resp:
            agent_out = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(agent_out["eye_reaction"], "coding")
        self.assertIn("public class Main", agent_out["response"])
        self.assertNotIn("```", agent_out["spoken_tts"])

    def test_03_mobile_html_has_handshake_overlay_and_fullscreen_eyeballs(self) -> None:
        html = Path("dashboard/mobile.html").read_text(encoding="utf-8")
        self.assertIn('id="connectHandshakeScreen"', html)
        self.assertIn('id="eyesStreamScreen"', html)
        self.assertIn('id="mobileEyeballCanvas"', html)
        self.assertIn("/eyeballs.js", html)
        self.assertIn("startAlwaysOnMic", html)
        self.assertNotIn("https://", html)


if __name__ == "__main__":
    unittest.main()
