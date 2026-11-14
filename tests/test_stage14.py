"""Stage 14 Verification Suite: Arduino Uno Firmware, Cubic Easing & Virtual Bot Simulator."""

from __future__ import annotations

import json
import unittest

from core.robotics.firmware_sim import VirtualArduinoBotSimulator, verify_ino_firmware_source


class TestStage14FirmwareAndVirtualSimulator(unittest.TestCase):
    def test_ino_firmware_supports_arduino_uno_cubic_easing_and_clamps(self) -> None:
        report = verify_ino_firmware_source("firmware/deskbot_avatar.ino")
        self.assertTrue(report["passed"], f"Firmware check failed: {report}")

    def test_virtual_arduino_uno_compact_and_json_packets_under_50ms(self) -> None:
        sim = VirtualArduinoBotSimulator(board_mode="arduino_uno")

        # 1. Test compact Arduino Uno frame <P135,T110,Elistening>
        frame = sim.encode_uno_compact_frame(135, 110, "listening")
        self.assertEqual(frame, "<P135,T110,Elistening>")
        ack1 = sim.process_packet(frame, now_ts=100.0)
        self.assertTrue(ack1["ack"])
        self.assertLess(ack1["latency_ms"], 50.0)
        self.assertEqual(ack1["target_pan"], 135)
        self.assertEqual(ack1["target_tilt"], 110)
        self.assertEqual(ack1["expression"], "listening")

        # Midpoint of 0.26s cubic move (t = 100.13s -> progress = 0.5)
        mid = sim.step(now_ts=100.13)
        self.assertAlmostEqual(mid["pan_deg"], 112.5, places=1)
        self.assertAlmostEqual(mid["tilt_deg"], 100.0, places=1)

        # End of move (t = 100.30s -> progress = 1.0)
        end = sim.step(now_ts=100.30)
        self.assertAlmostEqual(end["pan_deg"], 135.0, places=1)
        self.assertAlmostEqual(end["tilt_deg"], 110.0, places=1)

        # 2. Test JSON packet with extreme out-of-range angles clamped to [15, 165]
        ack2 = sim.process_packet(
            json.dumps({"eyes": {"expression": "happy"}, "servos": {"pan": 200, "tilt": -10}}),
            now_ts=101.0,
        )
        self.assertEqual(ack2["target_pan"], 165)
        self.assertEqual(ack2["target_tilt"], 15)

        # 3. Test 10s Bluetooth watchdog auto-reset to idle (90, 90)
        watchdog_state = sim.step(now_ts=112.5)
        self.assertEqual(watchdog_state["expression"], "idle")
        self.assertEqual(watchdog_state["target_pan"], 90)
        self.assertEqual(watchdog_state["target_tilt"], 90)


if __name__ == "__main__":
    unittest.main()
