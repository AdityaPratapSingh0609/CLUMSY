"""Stage 10 Verification Suite: Interactive 3D Robot Viewer & Real-Time Telemetry."""

from __future__ import annotations

from http.server import HTTPServer
import json
import threading
import time
import unittest
import urllib.request

from core.robot_bridge import RobotBridge
from core.robotics.kinematics import (
    clamp_servo_deg,
    compute_head_gaze_vector,
    ease_in_out_cubic,
    interpolate_pose,
    servo_deg_to_radians,
)
from dashboard.server import DeskbotRequestHandler


class TestStage10ViewerAndTelemetry(unittest.TestCase):
    def setUp(self) -> None:
        self.httpd = HTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2.0)

    def test_robot3d_asset_serves_and_contains_cad_parts_and_orbit_controls(self) -> None:
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/robot3d.js", timeout=2.0) as resp:
            js = resp.read().decode("utf-8")
            status = resp.status

        self.assertEqual(status, 200)
        self.assertIn("Deskbot3DViewer", js)
        for part in ("'base'", "'torso'", "'neck'", "'head'", "'oled_bezel'", "'eye_left'", "'eye_right'"):
            self.assertIn(part, js)
        for event_name in ("mousedown", "mousemove", "touchstart", "touchmove", "wheel", "dblclick"):
            self.assertIn(event_name, js)

    def test_forward_kinematics_and_cubic_easing(self) -> None:
        # Neutral gaze at (90°, 90°) points straight along +Z: (0, 0, 1)
        gx, gy, gz = compute_head_gaze_vector(90, 90)
        self.assertAlmostEqual(gx, 0.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)
        self.assertAlmostEqual(gz, 1.0, places=5)

        # Clamping protects plastic gears at [15°, 165°]
        self.assertEqual(clamp_servo_deg(-20), 15)
        self.assertEqual(clamp_servo_deg(220), 165)

        # Cubic easing boundary & midpoint checks
        self.assertAlmostEqual(ease_in_out_cubic(0.0), 0.0)
        self.assertAlmostEqual(ease_in_out_cubic(0.5), 0.5)
        self.assertAlmostEqual(ease_in_out_cubic(1.0), 1.0)

        p_mid, t_mid = interpolate_pose(90, 90, 130, 110, 0.5)
        self.assertAlmostEqual(p_mid, 110.0)
        self.assertAlmostEqual(t_mid, 100.0)

        yaw, pitch = servo_deg_to_radians(120, 75)
        self.assertLess(yaw, 0.0)
        self.assertGreater(pitch, 0.0)

    def test_posture_update_lag_under_5ms_and_http_telemetry_sync(self) -> None:
        bridge = RobotBridge(simulate=True)
        bridge.connect()

        t0 = time.perf_counter()
        bridge.set_thinking()
        telemetry = bridge.get_telemetry()
        lag_ms = (time.perf_counter() - t0) * 1000.0

        self.assertLess(lag_ms, 5.0, f"Posture update lag {lag_ms:.3f}ms exceeded 5ms budget")
        self.assertEqual(telemetry["pan_deg"], 105)
        self.assertEqual(telemetry["tilt_deg"], 115)
        self.assertEqual(telemetry["expression"], "thinking")

        # Verify HTTP POST /api/robot/telemetry round-trip and clamping
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/robot/telemetry",
            data=json.dumps({"expression": "listening", "pan": 180, "tilt": 10}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            updated = json.loads(resp.read().decode("utf-8"))

        self.assertEqual(updated["expression"], "listening")
        self.assertEqual(updated["pan_deg"], 165)
        self.assertEqual(updated["tilt_deg"], 15)


if __name__ == "__main__":
    unittest.main()
