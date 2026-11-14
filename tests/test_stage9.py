"""Stage 9 Verification Suite: Responsive Dashboard Core & 2D OLED Digital Twin."""

from __future__ import annotations

from http.server import HTTPServer
import json
from pathlib import Path
import re
import threading
import time
import unittest
import urllib.request

from core.robotics.kinematics import compute_oled_eye_state
from dashboard.server import DeskbotRequestHandler


class TestStage9DashboardAndOLED(unittest.TestCase):
    def setUp(self) -> None:
        self.httpd = HTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2.0)

    def test_dashboard_loads_under_100ms_with_zero_external_cdns(self) -> None:
        t0 = time.perf_counter()
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/index.html", timeout=2.0) as resp:
            html = resp.read().decode("utf-8")
            status = resp.status
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertEqual(status, 200)
        self.assertLess(elapsed_ms, 100.0, f"Dashboard load took {elapsed_ms:.2f}ms (> 100ms)")

        # Verify zero external http:// or https:// URLs in src= or href= attributes
        external_refs = re.findall(r'(?:src|href)\s*=\s*["\']https?://[^"\']+["\']', html, flags=re.IGNORECASE)
        self.assertEqual(external_refs, [], f"Found external CDN references: {external_refs}")

        # Verify core UI sections exist
        for required_id in (
            "view2D",
            "oledScreen",
            "leftEye",
            "rightEye",
            "messageList",
            "userInput",
            "nowPlaying",
            "deviceAvatar",
            "devicePhone",
            "deviceLaptop",
            "deviceDesktop",
        ):
            self.assertIn(f'id="{required_id}"', html)

        # Verify responsive breakpoints exist
        self.assertIn("@media (max-width: 1120px)", html)
        self.assertIn("@media (max-width: 760px)", html)

    def test_2d_oled_vector_eye_engine_states(self) -> None:
        idle = compute_oled_eye_state("idle", pan_deg=90, tilt_deg=90)
        self.assertEqual(idle["screen_width"], 128)
        self.assertEqual(idle["screen_height"], 64)
        self.assertEqual(idle["eye_shape"], "rounded_pupil")
        self.assertEqual(idle["pupil_offset"], {"dx": 0.0, "dy": 0.0})

        happy = compute_oled_eye_state("happy", pan_deg=90, tilt_deg=95)
        self.assertEqual(happy["eye_shape"], "arc_squint")
        self.assertLess(happy["left_eye"]["height"], idle["left_eye"]["height"])

        listening = compute_oled_eye_state("listening", pan_deg=90, tilt_deg=105)
        self.assertEqual(listening["eye_shape"], "wide_circle")
        self.assertGreater(listening["left_eye"]["height"], idle["left_eye"]["height"])

        confused = compute_oled_eye_state("confused", pan_deg=75, tilt_deg=80)
        self.assertEqual(confused["eye_shape"], "asymmetric")
        self.assertNotEqual(confused["left_eye"]["height"], confused["right_eye"]["height"])

        blinked = compute_oled_eye_state("idle", pan_deg=90, tilt_deg=90, blink_progress=1.0)
        self.assertEqual(blinked["left_eye"]["height"], 3.0)
        self.assertEqual(blinked["right_eye"]["height"], 3.0)

    def test_media_player_api_endpoint(self) -> None:
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/media",
            data=json.dumps({"action": "next"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(payload["status"], "playing")
        self.assertTrue(payload["track"])


if __name__ == "__main__":
    unittest.main()
