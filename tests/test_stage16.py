"""Stage 16 Verification Suite: Ultra-Dynamic Eyeball Engine (Irises, Dilating Pupils, Catchlights, Eyelids, Saccades & 12+ Reactions) + Bot Bluetooth & Mic."""

from __future__ import annotations

from pathlib import Path
import struct
import unittest

from core.bot_interactive import REACTION_CATALOG, BotInteractiveController


class TestStage16EyeballEngineAndBotReactions(unittest.TestCase):
    def test_01_eyeballs_js_and_12_plus_reactions_present(self) -> None:
        """Verify Bug Fix #4: dashboard/eyeballs.js implements full anatomical eyeballs & 12+ reactions."""
        eyeballs_js_path = Path(__file__).resolve().parent.parent / "dashboard" / "eyeballs.js"
        self.assertTrue(eyeballs_js_path.is_file(), "dashboard/eyeballs.js must exist")
        js_code = eyeballs_js_path.read_text(encoding="utf-8")

        self.assertIn("DeskbotEyeballEngine", js_code)
        self.assertIn("DESKBOT_REACTION_PRESETS", js_code)
        # Verify anatomical eyeball rendering layers
        for anatomy_keyword in ("scleraGrad", "irisGrad", "pupilRadius", "_drawHeartCatchlight", "upperClosure", "lowerClosure"):
            self.assertIn(anatomy_keyword, js_code)

        # Verify at least 12 distinct reactions in REACTION_CATALOG & eyeballs.js
        self.assertGreaterEqual(len(REACTION_CATALOG), 12)
        for rx in (
            "idle",
            "happy",
            "excited",
            "love",
            "listening",
            "thinking",
            "speaking",
            "coding",
            "wink",
            "surprised",
            "focused",
            "confused",
            "sleepy",
        ):
            self.assertIn(rx, REACTION_CATALOG)
            self.assertIn(f"{rx}:", js_code)

    def test_02_dashboard_mounts_eyeball_canvas_and_hides_uno_debug_tag(self) -> None:
        """Verify Bug Fix #4: No <P90,T95,Ehappy> debug string cluttering the OLED face."""
        index_path = Path(__file__).resolve().parent.parent / "dashboard" / "index.html"
        html = index_path.read_text(encoding="utf-8")

        self.assertIn('<script src="/eyeballs.js"></script>', html)
        self.assertIn('id="eyeballCanvas"', html)
        self.assertNotIn("&lt;P90,T90,Eidle&gt;", html)
        self.assertNotIn("unoTag.textContent = `<P", html)

    def test_03_bluetooth_connect_and_anatomical_eyeball_telemetry(self) -> None:
        bot = BotInteractiveController(board_mode="arduino_uno")
        bt_info = bot.connect_bluetooth(mode="virtual_bluetooth_uno")
        self.assertTrue(bt_info["bt_connected"])
        self.assertEqual(bt_info["board_mode"], "arduino_uno")
        self.assertTrue(bt_info["uno_ack"]["ack"])
        self.assertTrue(bt_info["eyeballs"]["has_eyeballs"])
        self.assertTrue(bt_info["eyeballs"]["has_irises"])
        self.assertTrue(bt_info["eyeballs"]["has_pupils"])
        self.assertTrue(bt_info["eyeballs"]["has_catchlights"])

        # Test cycling through multiple dynamic reactions
        for rx in ("happy", "excited", "love", "coding", "wink", "surprised", "focused", "listening"):
            pose_res = bot.send_bot_pose(expression=rx)
            self.assertEqual(pose_res["eyeballs"]["reaction"], rx)
            self.assertGreater(pose_res["eyeballs"]["pupil_radius_px"], 4.0)

    def test_04_live_microphone_activity_and_wake_word_reaction(self) -> None:
        bot = BotInteractiveController(board_mode="arduino_uno")

        loud_pcm = struct.pack("<320h", *([3200] * 320))
        mic_state = bot.process_mic_frame(
            pcm16_bytes=loud_pcm,
            simulated_text="Hey Jarvis, play synthwave music",
        )
        self.assertTrue(mic_state["speech_active"])
        self.assertTrue(mic_state["wake_detected"])
        self.assertEqual(mic_state["transcript"], "play synthwave music")
        self.assertEqual(len(mic_state["waveform_bars"]), 16)
        self.assertEqual(bot.robot_bridge.current_expression, "listening")
        # Pupil dilates when listening to active voice
        self.assertGreater(mic_state["eyeballs"]["pupil_scale"], 1.2)


if __name__ == "__main__":
    unittest.main()
