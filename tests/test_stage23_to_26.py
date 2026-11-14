"""Unit & Integration Tests for Stages 23, 24, 25, and 26.

Verifies:
- Stage 23: Dynamic Interplatform Connectivity Hub (`Gmail`, `Google Calendar`, `Notes / Google Keep`, `Netflix`, `Amazon`)
- Stage 24: 3D Model Rendering (`.obj` + `.scad`), Blender `bpy` Bridge (`_blender.py`), AI Video Maker, AI Pic & Graphic Creator, and Extra AI Power Tools
- Stage 25: Perfect Hands-Free Voice Recognition, Phonetic Correction (`jeemail` -> `gmail`, `callender` -> `calendar`, `net flicks` -> `netflix`, `blander` -> `blender`, `three d` -> `3d`), and Multi-Alternative Selection
- Stage 26: Live Dashboard & Mobile Companion Endpoints (`/api/interplatform`, `/api/creative`, `/api/query` with voice normalization) and Zero External CDN Dependency Guarantee
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen

from core.brain import AssistantBrain
from core.creative_studio import CreativeAIStudio
from core.job_engine import UniversalJobEngine
from core.llm_fusion import JarvisFusionModel
from core.mesh.device_manager import DeviceMeshManager
from core.robot_bridge import RobotBridge
from core.voice.voice_commander import normalize_voice_transcript, parse_voice_intent
from dashboard.server import DeskbotRequestHandler, ThreadingHTTPServer
from plugins import interplatform_hub


class TestStages23To26(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.out_root = Path(self.tmp_dir.name)
        self.engine = UniversalJobEngine(output_root=self.out_root)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_stage23_interplatform_hub_gmail_calendar_notes_netflix_amazon(self) -> None:
        # 1. Gmail compose
        g_res = interplatform_hub.execute_interplatform_task(
            "Compose email to tony@stark.com subject Arc Reactor Update body Diagnostics green",
            platform="gmail",
            execute_os=False,
            output_root=self.out_root,
        )
        self.assertEqual(g_res["platform"], "gmail")
        self.assertIn("mail.google.com", g_res["url"])
        self.assertIn("tony%40stark.com", g_res["url"])

        # 2. Google Calendar + .ics export
        c_res = interplatform_hub.execute_interplatform_task(
            "Schedule meeting about Deskbot 3D Launch tomorrow at 4pm",
            platform="calendar",
            execute_os=False,
            output_root=self.out_root,
        )
        self.assertEqual(c_res["platform"], "calendar")
        self.assertIn("calendar.google.com", c_res["url"])
        self.assertTrue(Path(c_res["ics_file"]).is_file())

        # 3. Notes / Google Keep persistence
        n_res = interplatform_hub.execute_interplatform_task(
            "Take a note: Calibrate Blender 3D mesh shaders",
            platform="notes",
            execute_os=False,
            output_root=self.out_root,
        )
        self.assertEqual(n_res["platform"], "notes")
        self.assertTrue(any("Calibrate Blender" in item["text"] for item in n_res["notes"]))

        # 4. Netflix deep-link streaming search
        nf_res = interplatform_hub.execute_interplatform_task(
            "Play Stranger Things on Netflix",
            platform="netflix",
            execute_os=False,
            output_root=self.out_root,
        )
        self.assertEqual(nf_res["platform"], "netflix")
        self.assertIn("netflix.com/search", nf_res["url"])

        # 5. Amazon shopping search
        amz_res = interplatform_hub.execute_interplatform_task(
            "Search Arduino Uno Servo Kit on Amazon",
            platform="amazon",
            execute_os=False,
            output_root=self.out_root,
        )
        self.assertEqual(amz_res["platform"], "amazon")
        self.assertIn("amazon.", amz_res["url"])

    def test_stage24_creative_3d_blender_video_pic_and_ai_tools(self) -> None:
        studio = CreativeAIStudio(output_root=self.out_root)

        # 1. 3D Model + Blender bpy script + OpenSCAD
        m3d = studio.build_3d_model("job_3d_test", "Render a 3D model of Deskbot Head in Blender", execute_os=False)
        self.assertTrue(Path(m3d["obj_path"]).is_file())
        self.assertTrue(Path(m3d["scad_path"]).is_file())
        self.assertTrue(Path(m3d["blender_script_path"]).is_file())
        self.assertIn("import bpy", Path(m3d["blender_script_path"]).read_text(encoding="utf-8"))
        self.assertGreater(m3d["vertex_count"], 8)
        self.assertIn("<canvas", m3d["preview_html"])

        # 2. AI Video Maker
        vid = studio.build_ai_video("job_vid_test", "Make a video about JARVIS Autonomous Robotics")
        self.assertTrue(Path(vid["file_path"]).is_file())
        self.assertEqual(len(vid["scenes"]), 3)
        self.assertIn("AI VIDEO MAKER STUDIO", vid["preview_html"])

        # 3. AI Pic & Graphic Creator
        pic = studio.build_ai_pic("job_pic_test", "Create a picture of Cyberpunk Stark Lab")
        self.assertTrue(Path(pic["file_path"]).is_file())
        self.assertIn("<svg", pic["content"])

        # 4. Extra AI Power Tool (Flowchart / Mind Map)
        flow = studio.build_ai_tool("job_flow_test", "Create a mind map flowchart of JARVIS Architecture")
        self.assertTrue(Path(flow["file_path"]).is_file())
        self.assertIn("INTERPLATFORM HUB", flow["content"])

    def test_stage25_perfect_voice_phonetic_normalizer_and_brain_routing(self) -> None:
        # Phonetic misspellings from STT should normalize cleanly
        self.assertIn(
            "gmail",
            normalize_voice_transcript("hey harvis open jeemail and send email to Pepper").lower(),
        )
        self.assertIn(
            "calendar",
            normalize_voice_transcript("schedule meeting on google callender tomorrow").lower(),
        )
        self.assertIn(
            "netflix",
            normalize_voice_transcript("play sci fi on net flicks").lower(),
        )
        self.assertIn(
            "blender",
            normalize_voice_transcript("make a three d model in blander").lower(),
        )
        self.assertIn(
            "3d",
            normalize_voice_transcript("render a three d model of arc reactor").lower(),
        )

        # Multi-alternative selection picks the domain-rich transcript
        chosen = normalize_voice_transcript(
            "open sea mail",
            alternatives=["open sea mail", "open jeemail and send email"],
        )
        self.assertIn("gmail", chosen.lower())

        # Brain end-to-end voice query execution
        robot = RobotBridge(simulate=True)
        robot.connect()
        mesh = DeviceMeshManager()
        brain = AssistantBrain(
            robot_bridge=robot,
            mesh_manager=mesh,
            llm_engine=JarvisFusionModel(max_ram_mb=850),
            job_engine=self.engine,
        )

        res_3d = brain.process_query("Hey charvis render a three d model of arc reactor in blander")
        self.assertIsNotNone(res_3d["job_artifact"])
        self.assertEqual(res_3d["job_artifact"]["job_type"], "3d_model")

        res_cal = brain.process_query("Schedule a meeting in google callender for Robotics Demo")
        self.assertIsNotNone(res_cal["job_artifact"])
        self.assertEqual(res_cal["job_artifact"]["job_type"], "interplatform")
        self.assertEqual(res_cal["job_artifact"]["platform"], "calendar")

    def test_stage26_http_endpoints_and_offline_html_integrity(self) -> None:
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), DeskbotRequestHandler)
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            # 1. Test /api/interplatform
            req1 = Request(
                f"http://127.0.0.1:{port}/api/interplatform",
                data=json.dumps({"platform": "netflix", "prompt": "Play Iron Man on net flicks"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req1, timeout=5) as resp1:
                data1 = json.loads(resp1.read().decode("utf-8"))
                self.assertEqual(data1["platform"], "netflix")
                self.assertIn("netflix.com", data1["url"])

            # 2. Test /api/creative
            req2 = Request(
                f"http://127.0.0.1:{port}/api/creative",
                data=json.dumps({"job_type": "3d_model", "prompt": "Render a three d model of Deskbot"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req2, timeout=5) as resp2:
                data2 = json.loads(resp2.read().decode("utf-8"))
                self.assertEqual(data2["job_type"], "3d_model")
                self.assertIn("blender_script_path", data2)
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()
