"""Stage 13 Verification Suite: Arduino Uno & ESP32 Circuit, Pinout & Power Budget."""

from __future__ import annotations

from pathlib import Path
import unittest

from core.robotics.circuit_verifier import verify_circuit_profile


class TestStage13CircuitAndPower(unittest.TestCase):
    def test_arduino_uno_circuit_pinout_and_power_budget(self) -> None:
        report = verify_circuit_profile("arduino_uno")
        self.assertTrue(report["passed"], f"Arduino Uno circuit check failed: {report}")
        self.assertTrue(report["unique_pins"])
        self.assertTrue(report["pwm_ok"])
        self.assertTrue(report["i2c_ok"])
        self.assertTrue(report["decoupling_ok"])
        self.assertEqual(report["pins"]["oled_sda"], "A4")
        self.assertEqual(report["pins"]["oled_scl"], "A5")
        self.assertEqual(report["pins"]["pan_servo_pwm"], "D9")
        self.assertEqual(report["pins"]["tilt_servo_pwm"], "D10")
        self.assertGreaterEqual(report["servo_rail_v"], 4.95)
        self.assertEqual(report["logic_3v3_v"], 3.3)

    def test_esp32_circuit_pinout_and_power_budget(self) -> None:
        report = verify_circuit_profile("esp32")
        self.assertTrue(report["passed"], f"ESP32 circuit check failed: {report}")
        self.assertEqual(report["pins"]["oled_sda"], "GPIO21")
        self.assertEqual(report["pins"]["oled_scl"], "GPIO22")
        self.assertGreaterEqual(report["servo_rail_v"], 4.95)

    def test_hardware_list_documents_arduino_uno_and_220uf_capacitor(self) -> None:
        hw_doc = Path("HARDWARE_LIST.md").read_text(encoding="utf-8")
        self.assertIn("Arduino Uno", hw_doc)
        self.assertIn("Pin D9", hw_doc)
        self.assertIn("Pin D10", hw_doc)
        self.assertIn("220µF", hw_doc)


if __name__ == "__main__":
    unittest.main()
