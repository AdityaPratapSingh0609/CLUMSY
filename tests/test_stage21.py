"""Stage 21 Verification Suite: Universal 'Do-Anything' Laptop Action Engine (Apps, Websites, Songs, PPT & SVG Studio)."""

from __future__ import annotations

import tempfile
import unittest

from core.brain import AssistantBrain
from core.job_engine import UniversalJobEngine
from core.mesh.device_manager import DeviceMeshManager
from core.robot_bridge import RobotBridge
from plugins import app_launcher, media_player


class TestStage21UniversalLaptopActionEngine(unittest.TestCase):
    def test_01_universal_app_and_website_launcher(self) -> None:
        for app_name, expected_cmd in (
            ("Spotify", "spotify:"),
            ("VS Code", "code"),
            ("YouTube", "https://www.youtube.com"),
            ("Calculator", "calc.exe"),
            ("Terminal", "wt.exe"),
            ("File Explorer", "explorer.exe"),
        ):
            res = app_launcher.handle_app_launcher(
                {"target": "desktop_host", "app_name": app_name, "execute_os": False}
            )
            self.assertTrue(res["success"])
            self.assertEqual(res["resolved_command"], expected_cmd)

    def test_02_custom_song_playback_and_multimodal_jobs(self) -> None:
        # 1. Play a specific requested song on system audio
        song_res = media_player.handle_media_player({"action": "play", "track": "Iron Man Back In Black"})
        self.assertEqual(song_res["status"], "playing")
        self.assertEqual(song_res["track"], "Iron Man Back In Black")

        # 2. Execute PPT, SVG Graphic, and Executive Brief via UniversalJobEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = UniversalJobEngine(output_root=tmpdir)
            ppt = engine.execute_job("Make a PPT presentation on Quantum Computing")
            self.assertEqual(ppt["job_type"], "ppt")
            self.assertEqual(len(ppt["slides"]), 3)

            svg = engine.execute_job("Create a vector graphic logo for Stark Industries")
            self.assertEqual(svg["job_type"], "graphic")
            self.assertIn("<svg", svg["content"])

            doc = engine.execute_job("Write an executive briefing on Deskbot")
            self.assertEqual(doc["job_type"], "document")

    def test_03_brain_routes_app_launch_and_music_commands(self) -> None:
        robot = RobotBridge(simulate=True)
        robot.connect()
        mesh = DeviceMeshManager()
        brain = AssistantBrain(robot_bridge=robot, mesh_manager=mesh)

        yt = brain.process_query("Open YouTube on my laptop")
        self.assertEqual(yt["action"]["tool"], "launch_app")

        song = brain.process_query("Play song Cyberpunk Arc Reactor")
        self.assertEqual(song["action"]["tool"], "media_player")
        self.assertIsNotNone(song["job_artifact"])


if __name__ == "__main__":
    unittest.main()
