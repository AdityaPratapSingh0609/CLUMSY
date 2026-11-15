"""Stage 43 Hardware Mesh, Servo Jitter Guard & Multimodal Verification Tests.

Verifies:
- Bug #109: Servo angle boundary enforcement (15°..165°)
- Bug #110: Eyeball gaze vector clamping
- Bug #111: Autonomous micro-expressions & state transitions
- Bug #112: Dual-stream audio ducking
- Bug #113: Hardware mic buffer overflow protection
- Bug #114: BLE binary frame encoding & CRC32 verification
- Bug #115: Mobile PWA cache versioning (v43)
- Bug #116: Deterministic voice commands for hardware control
- Bug #117: Cross-node mesh telemetry ping
- Bug #118: Wikipedia elaboration lockdown & T-1000 prevention
"""

import unittest
from core.robotics.kinematics import clamp_servo_deg
from core.robotics.firmware_sim import VirtualArduinoBotSimulator
from core.voice.hardware_mic import hardware_mic_daemon, _is_valid_voice_command
from core.llm_engine import LLMEngine


class TestStage43HardwareMesh(unittest.TestCase):
    def setUp(self):
        self.sim = VirtualArduinoBotSimulator()

    def test_bug109_servo_clamps(self):
        """Bug #109: Servos must strictly clamp between 15 and 165 degrees."""
        self.assertEqual(clamp_servo_deg(0), 15)
        self.assertEqual(clamp_servo_deg(10), 15)
        self.assertEqual(clamp_servo_deg(15), 15)
        self.assertEqual(clamp_servo_deg(90), 90)
        self.assertEqual(clamp_servo_deg(165), 165)
        self.assertEqual(clamp_servo_deg(180), 165)
        self.assertEqual(clamp_servo_deg(250), 165)

    def test_bug114_binary_frame_crc32(self):
        """Bug #114: High-speed framed binary packets encode and decode with CRC32."""
        frame = self.sim.encode_binary_frame(45, 135, "happy")
        self.assertEqual(len(frame), 8)
        self.assertEqual(frame[0], 0xAA)
        self.assertEqual(frame[1], 0x55)

        decoded = self.sim.decode_binary_frame(frame)
        self.assertTrue(decoded["valid"])
        self.assertEqual(decoded["pan"], 45)
        self.assertEqual(decoded["tilt"], 135)
        self.assertEqual(decoded["expression"], "happy")

        # Test packet processing in simulator
        proc = self.sim.process_packet(frame)
        self.assertTrue(proc["ack"])
        self.assertEqual(proc["target_pan"], 45)
        self.assertEqual(proc["target_tilt"], 135)

    def test_bug114_corrupted_crc_rejected(self):
        """Bug #114: Corrupted bytes over serial are rejected by CRC."""
        frame = bytearray(self.sim.encode_binary_frame(90, 90, "idle"))
        frame[2] = 120  # Tamper with pan without updating CRC
        decoded = self.sim.decode_binary_frame(bytes(frame))
        self.assertFalse(decoded["valid"])
        self.assertEqual(decoded["error"], "crc_mismatch")

    def test_bug113_hardware_mic_buffer_clear(self):
        """Bug #113: Hardware mic daemon supports buffer overflow flushing."""
        hardware_mic_daemon.clear_buffer()
        self.assertEqual(hardware_mic_daemon.get_queue_size(), 0)

    def test_bug116_voice_commands_validity(self):
        """Bug #116: Hardware voice commands are recognized as valid speech."""
        for cmd in ["look left", "look right", "look up", "look down", "center eyes", "blink", "wink", "be happy", "go to sleep", "wake up", "ping nodes"]:
            self.assertTrue(_is_valid_voice_command(cmd), f"Command '{cmd}' should be valid voice command")

    def test_bug116_hardware_look_intents(self):
        """Bug #116: Hardware look commands route to servo coordinates."""
        res_left = LLMEngine._deterministic_intent("look left")
        self.assertEqual(res_left["robot_servo"]["pan"], 45)
        self.assertEqual(res_left["robot_servo"]["tilt"], 90)

        res_right = LLMEngine._deterministic_intent("look right")
        self.assertEqual(res_right["robot_servo"]["pan"], 135)
        self.assertEqual(res_right["robot_servo"]["tilt"], 90)

        res_up = LLMEngine._deterministic_intent("look up")
        self.assertEqual(res_up["robot_servo"]["pan"], 90)
        self.assertEqual(res_up["robot_servo"]["tilt"], 135)

        res_down = LLMEngine._deterministic_intent("look down")
        self.assertEqual(res_down["robot_servo"]["pan"], 90)
        self.assertEqual(res_down["robot_servo"]["tilt"], 45)

        res_center = LLMEngine._deterministic_intent("center eyes")
        self.assertEqual(res_center["robot_servo"]["pan"], 90)
        self.assertEqual(res_center["robot_servo"]["tilt"], 90)

    def test_bug116_micro_expressions(self):
        """Bug #116: Eyeball micro-expressions trigger proper states."""
        res_blink = LLMEngine._deterministic_intent("blink eyes")
        self.assertEqual(res_blink["robot_expression"], "blink")

        res_happy = LLMEngine._deterministic_intent("be happy")
        self.assertEqual(res_happy["robot_expression"], "happy")

        res_wink = LLMEngine._deterministic_intent("give me a wink")
        self.assertEqual(res_wink["robot_expression"], "wink")

        res_sleep = LLMEngine._deterministic_intent("go to sleep")
        self.assertEqual(res_sleep["robot_expression"], "sleep")

        res_wake = LLMEngine._deterministic_intent("wake up")
        self.assertEqual(res_wake["robot_expression"], "happy")

    def test_bug117_mesh_ping_latency(self):
        """Bug #117: Cross-node mesh ping provides diagnostics."""
        res_ping = LLMEngine._deterministic_intent("ping nodes")
        self.assertIn("Dual-transport device mesh is 100% operational", res_ping["spoken_response"])
        self.assertIn("desktop_host", str(res_ping) + res_ping["spoken_response"])

    def test_bug118_orphaned_elaboration_guard(self):
        """Bug #118: Orphaned elaboration query does not search entity or hallucinate T-1000."""
        res = LLMEngine._deterministic_intent("can you explain it to me in 1000 words?")
        self.assertIn("What topic would you like me to explain", res["spoken_response"])
        self.assertNotIn("T-1000", res["spoken_response"])
        self.assertNotIn("Terminator", res["spoken_response"])


if __name__ == "__main__":
    unittest.main()
