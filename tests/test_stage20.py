"""Stage 20 Verification Suite: Always-On Background Daemon, Auto-Connect Persistence & Smart Device Audio Routing."""

from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
import tempfile
from pathlib import Path
import threading
import unittest
import urllib.request

from dashboard.server import DeskbotRequestHandler
from scripts.jarvis_background import JarvisBackgroundDaemon


class TestStage20BackgroundDaemonAndAudioRouting(unittest.TestCase):
    def setUp(self) -> None:
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2.0)

    def test_01_background_daemon_state_persistence_and_speaker_routing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / ".deskbot_state.json"
            daemon = JarvisBackgroundDaemon(state_file=state_path)
            self.assertTrue(daemon.running_in_background)
            self.assertTrue(daemon.always_on_mic)

            # Smart source-device audio routing: speaking on phone routes TTS to phone speaker
            phone_route = daemon.resolve_speaker_targets("mobile_app")
            self.assertTrue(phone_route["play_on_phone"])
            self.assertFalse(phone_route["play_on_laptop"])

            # Speaking on laptop routes TTS to laptop speaker
            laptop_route = daemon.resolve_speaker_targets("laptop_hub")
            self.assertTrue(laptop_route["play_on_laptop"])
            self.assertFalse(laptop_route["play_on_phone"])

            # Toggle to 'both' and verify persistence across restart
            daemon.configure(voice_output_target="both")
            reloaded = JarvisBackgroundDaemon(state_file=state_path)
            self.assertEqual(reloaded.voice_output_target, "both")
            both_route = reloaded.resolve_speaker_targets("mobile_app")
            self.assertTrue(both_route["play_on_phone"])
            self.assertTrue(both_route["play_on_laptop"])

    def test_02_background_http_endpoints_and_heartbeat(self) -> None:
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/background/status", timeout=2.0) as resp:
            status = json.loads(resp.read().decode("utf-8"))
        self.assertTrue(status["running_in_background"])

        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/background/config",
            data=json.dumps({"heartbeat": True, "device_id": "phone_eyes_app"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            hb = json.loads(resp.read().decode("utf-8"))
        self.assertGreaterEqual(hb["heartbeat_count"], 1)


if __name__ == "__main__":
    unittest.main()
