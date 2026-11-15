"""
Stage 46 Omni Telemetry, Multilingual Translation, Timezone & Physics Tests
Validates Bugs #145–#156:
- Bug #145: Multi-Lingual Translation & Cross-Lingual Semantic Engine (10 languages)
- Bug #146: Global Timezone Converter & World Clock Math
- Bug #147: Multi-Dimensional Physics Unit Converter (Speed, Pressure, Energy, Storage)
- Bug #148: Deep System Telemetry & Process Inspector
- Bug #149: Offline Reminder & Countdown Timer Scheduler
"""

import unittest
from core.llm_engine import LLMEngine


class TestStage46OmniTelemetryMultilingual(unittest.TestCase):
    def setUp(self):
        self.engine = LLMEngine(model_path=None)

    def test_multilingual_translation_intent(self):
        """Bug #145: Translation intent detection for diverse languages."""
        r1 = self.engine.generate("translate hello to Spanish")
        self.assertEqual(r1["tool_call"]["tool"], "answer_query")
        self.assertEqual(r1["tool_call"]["params"]["topic"], "translation")
        self.assertEqual(r1["tool_call"]["params"]["phrase"], "hello")
        self.assertEqual(r1["tool_call"]["params"]["target_language"].lower(), "spanish")

        r2 = self.engine.generate("how do you say thank you in French")
        self.assertEqual(r2["tool_call"]["tool"], "answer_query")
        self.assertEqual(r2["tool_call"]["params"]["topic"], "translation")
        self.assertEqual(r2["tool_call"]["params"]["phrase"], "thank you")
        self.assertEqual(r2["tool_call"]["params"]["target_language"].lower(), "french")

        r3 = self.engine.generate("what does arigatou mean in english")
        self.assertEqual(r3["tool_call"]["tool"], "answer_query")
        self.assertEqual(r3["tool_call"]["params"]["topic"], "translation")
        self.assertEqual(r3["tool_call"]["params"]["phrase"], "arigatou")

    def test_global_timezone_difference_and_clock(self):
        """Bug #146: Timezone offset difference and city clock queries."""
        r1 = self.engine.generate("time difference between New York and London")
        self.assertEqual(r1["tool_call"]["tool"], "answer_query")
        self.assertEqual(r1["tool_call"]["params"]["topic"], "timezone")
        self.assertEqual(r1["tool_call"]["params"]["action"], "difference")

        r2 = self.engine.generate("what time is it in Tokyo?")
        self.assertEqual(r2["tool_call"]["tool"], "answer_query")
        self.assertEqual(r2["tool_call"]["params"]["topic"], "world_clock")
        self.assertEqual(r2["tool_call"]["params"]["city"].lower(), "tokyo")

    def test_speed_unit_conversion(self):
        """Bug #147: Speed conversions (m/s <-> km/h, knots <-> mph)."""
        res_ms = self.engine._try_solve_math("convert 100 m/s to km/h")
        self.assertIsNotNone(res_ms)
        self.assertIn("360 km/h", res_ms)

        res_kmh = self.engine._try_solve_math("convert 36 km/h to m/s")
        self.assertIsNotNone(res_kmh)
        self.assertIn("10 m/s", res_kmh)

        res_kts = self.engine._try_solve_math("convert 50 knots to mph")
        self.assertIsNotNone(res_kts)
        self.assertIn("57.538", res_kts)

    def test_pressure_unit_conversion(self):
        """Bug #147: Fluid pressure conversions (atm <-> psi, bar <-> Pa, kPa <-> psi)."""
        res_atm = self.engine._try_solve_math("convert 2 atm to psi")
        self.assertIsNotNone(res_atm)
        self.assertIn("29.3919", res_atm)

        res_bar = self.engine._try_solve_math("convert 5 bar to pa")
        self.assertIsNotNone(res_bar)
        self.assertIn("500,000 Pa", res_bar)

        res_kpa = self.engine._try_solve_math("convert 100 kpa to psi")
        self.assertIsNotNone(res_kpa)
        self.assertIn("14.5038", res_kpa)

    def test_energy_unit_conversion(self):
        """Bug #147: Thermodynamic & electrical energy (cal <-> J, kWh <-> J)."""
        res_cal = self.engine._try_solve_math("convert 500 cal to joules")
        self.assertIsNotNone(res_cal)
        self.assertIn("2092 Joules", res_cal)

        res_kwh = self.engine._try_solve_math("convert 10 kwh to joules")
        self.assertIsNotNone(res_kwh)
        self.assertIn("36,000,000 Joules", res_kwh)

    def test_digital_storage_conversion(self):
        """Bug #147: Digital storage conversions (GB <-> MB, TB <-> GB)."""
        res_gb = self.engine._try_solve_math("convert 16 gb to mb")
        self.assertIsNotNone(res_gb)
        self.assertIn("16,384 MB", res_gb)

        res_tb = self.engine._try_solve_math("convert 2 tb to gb")
        self.assertIsNotNone(res_tb)
        self.assertIn("2,048 GB", res_tb)

    def test_deep_system_telemetry_intents(self):
        """Bug #148: Deep system telemetry and process inspection."""
        r1 = self.engine.generate("top memory processes")
        self.assertEqual(r1["tool_call"]["tool"], "answer_query")
        self.assertEqual(r1["tool_call"]["params"]["topic"], "system_telemetry")
        self.assertEqual(r1["tool_call"]["params"]["metric"], "top_processes")

        r2 = self.engine.generate("disk partition geometries")
        self.assertEqual(r2["tool_call"]["tool"], "answer_query")
        self.assertEqual(r2["tool_call"]["params"]["topic"], "system_telemetry")
        self.assertEqual(r2["tool_call"]["params"]["metric"], "disk_partitions")

        r3 = self.engine.generate("network host ip")
        self.assertEqual(r3["tool_call"]["tool"], "answer_query")
        self.assertEqual(r3["tool_call"]["params"]["topic"], "system_telemetry")
        self.assertEqual(r3["tool_call"]["params"]["metric"], "network_ip")

        r4 = self.engine.generate("system uptime")
        self.assertEqual(r4["tool_call"]["tool"], "answer_query")
        self.assertEqual(r4["tool_call"]["params"]["topic"], "system_telemetry")
        self.assertEqual(r4["tool_call"]["params"]["metric"], "uptime")

    def test_countdown_timer_scheduler(self):
        """Bug #149: Countdown timer scheduling and cancellation."""
        r1 = self.engine.generate("set a timer for 5 minutes")
        self.assertEqual(r1["tool_call"]["tool"], "answer_query")
        self.assertEqual(r1["tool_call"]["params"]["topic"], "timer_manager")
        self.assertEqual(r1["tool_call"]["params"]["action"], "set")
        self.assertEqual(r1["tool_call"]["params"]["amount"], "5")

        r2 = self.engine.generate("list active timers")
        self.assertEqual(r2["tool_call"]["tool"], "answer_query")
        self.assertEqual(r2["tool_call"]["params"]["topic"], "timer_manager")
        self.assertEqual(r2["tool_call"]["params"]["action"], "list")

        r3 = self.engine.generate("cancel all timers")
        self.assertEqual(r3["tool_call"]["tool"], "answer_query")
        self.assertEqual(r3["tool_call"]["params"]["topic"], "timer_manager")
        self.assertEqual(r3["tool_call"]["params"]["action"], "cancel_all")

    def test_financial_compound_interest_regression_intact(self):
        """Stage 45 regression check: compound interest remains fully intact."""
        math_res = self.engine._try_solve_math("compound interest on $1000 at 5% for 3 years")
        self.assertIsNotNone(math_res)
        self.assertIn("1,157.63", math_res)


if __name__ == "__main__":
    unittest.main()
