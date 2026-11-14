"""Tests for Stages 27-30: laptop auto-launch streaming, rich 3D CAD meshes, photo studio, emotion eye colours."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest import mock

from core.creative_studio import CreativeAIStudio, detect_3d_shape
from core.voice.voice_commander import parse_voice_intent
from plugins import interplatform_hub

ROOT = Path(__file__).resolve().parent.parent


class TestStages27To30(unittest.TestCase):
    def test_stage27_streaming_title_extraction_and_laptop_launch(self) -> None:
        cases = [
            ("Hey bot I want to play Stranger Things on Netflix", "netflix", "netflix.com/search?q=Stranger%20Things"),
            ("Play The Boys on Amazon Prime Video", "prime_video", "primevideo.com"),
            ("Hey bot play Loki on Hotstar", "hotstar", "hotstar.com"),
        ]
        for prompt, plat, url_part in cases:
            with mock.patch.object(interplatform_hub, "launch_url_on_laptop", return_value=True) as launcher:
                res = interplatform_hub.execute_interplatform_task(prompt, execute_os=True)
            self.assertEqual(res["platform"], plat, prompt)
            self.assertIn(url_part, res["url"], prompt)
            self.assertTrue(res["launched_on_laptop"])
            launcher.assert_called_once_with(res["url"])

        self.assertEqual(interplatform_hub._extract_streaming_title(
            "Hey bot I want to play Stranger Things on Netflix", "netflix"), "Stranger Things")

        intent = parse_voice_intent("hey bot play the boys on amazon prime")
        self.assertEqual(intent["platform"], "prime_video")

    def test_stage28_rich_engineering_meshes(self) -> None:
        self.assertEqual(detect_3d_shape("engineering model of a building"), "engineering_building")
        self.assertEqual(detect_3d_shape("3d suspension bridge"), "suspension_bridge")
        self.assertEqual(detect_3d_shape("3d quadcopter drone"), "quadcopter_drone")
        self.assertEqual(detect_3d_shape("3d model of a teapot"), "universal_custom")
        with tempfile.TemporaryDirectory() as tmp:
            studio = CreativeAIStudio(output_root=tmp)
            for prompt in ("Create an engineering 3D model of a skyscraper building",
                           "3D model of a suspension bridge", "3D robotic arm", "3D model of a teapot"):
                res = studio.build_3d_model("t", prompt)
                self.assertGreater(res["vertex_count"], 80, prompt)
                self.assertTrue(Path(res["blender_script_path"]).is_file())

    def test_stage29_photo_studio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = CreativeAIStudio(output_root=tmp).build_ai_pic("p", "Generate a realistic photo of sunset on Goa beach")
            self.assertIn("image.pollinations.ai", res["cloud_ai_url"])
            self.assertIn("<canvas", res["preview_html"])
            self.assertTrue(Path(res["file_path"]).is_file())

    def test_stage30_emotion_colours_differ(self) -> None:
        js = (ROOT / "dashboard" / "eyeballs.js").read_text(encoding="utf-8")
        self.assertIn("browColor", js)
        self.assertIn("scleraRim", js)
        # happy must no longer reuse idle cyan
        happy_block = js.split("happy: {", 1)[1].split("},", 1)[0]
        self.assertNotIn("#38bdf8", happy_block)


if __name__ == "__main__":
    unittest.main()
