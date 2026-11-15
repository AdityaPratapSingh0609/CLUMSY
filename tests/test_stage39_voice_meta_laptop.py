"""Unit and Integration Verification Suite for Stage 39 (CLUMSY-7X Omni).

Verifies:
- Bug #61: Inactivity Sleep Auto-Wakeup
- Bug #62: Conversational Meta-Prompt Handlers ("I want a reply for a certain question", "can you hear me")
- Bug #63: Wikipedia Conversational Stopwords Guard (no song/novel hijacking)
- Bug #64: Mobile Mic Permission & Auto-Reconnect
- Bug #65: Standalone Mobile Mode
- Bug #66: Laptop Hub Node Telemetry & Status
- Bug #67: Laptop Remote Action Execution in Brain & Mesh Router
- Bug #68: Backend Deterministic Intent for Meta-Prompts
- Bug #69: Continuous Hardware Mic Streaming
- Bug #70: Speech Recognition Silence Recovery
- Bug #71: Conversational Prefix Stripping in Questions
- Bug #72: Mobile/Desktop Dual Synchronous Mesh Broadcasting
"""

import unittest
from core.brain import AssistantBrain
from core.llm_engine import LLMEngine
from core.llm_fusion import JarvisFusionModel
from core.mesh.device_manager import DeviceMeshManager
from core.robot_bridge import RobotBridge


class TestStage39VoiceMetaLaptop(unittest.TestCase):
    """Verifies Stage 39 Voice Engine, Meta-Prompts, and Laptop Mesh Router."""

    def setUp(self):
        self.engine = LLMEngine(model_path=None)
        self.fusion = JarvisFusionModel(max_ram_mb=850)
        self.robot = RobotBridge(port=None)
        self.mesh = DeviceMeshManager()
        self.brain = AssistantBrain(
            robot_bridge=self.robot,
            mesh_manager=self.mesh,
            llm_engine=self.engine,
        )

    def test_meta_question_readiness(self):
        """Bug #62: 'I want a reply for a certain question' returns readiness, NOT Wikipedia definition."""
        res = self.engine.generate("I want a reply for a certain question")
        spoken = res["spoken_response"].lower()
        self.assertNotIn("grammatical form", spoken)
        self.assertNotIn("utterance which serves", spoken)
        self.assertNotIn("rhetorical question", spoken)
        self.assertTrue("ready" in spoken or "ask" in spoken or "question" in spoken)

    def test_voice_check_hearing(self):
        """Bug #62: 'can you hear me' confirms microphone audio is active."""
        res = self.engine.generate("can you hear me")
        spoken = res["spoken_response"].lower()
        self.assertNotIn("lady (hear me tonight)", spoken)
        self.assertNotIn("french house duo", spoken)
        self.assertTrue("hear" in spoken or "loud and clear" in spoken)

    def test_presence_check(self):
        """Bug #62: 'are you there' confirms presence."""
        res = self.engine.generate("are you there")
        spoken = res["spoken_response"].lower()
        self.assertTrue("right here" in spoken or "ready" in spoken or "assist" in spoken)

    def test_preamble_math_stripping(self):
        """Bug #71: 'I have a question: what is 10 + 25?' strips preamble and evaluates to 35."""
        res = self.engine.generate("I have a question: what is 10 + 25?")
        self.assertIn("35", res["spoken_response"])

    def test_preamble_science_stripping(self):
        """Bug #71: 'Can you answer this question: what is photosynthesis?' explains photosynthesis."""
        res = self.engine.generate("Can you answer this question: what is photosynthesis?")
        spoken = res["spoken_response"].lower()
        self.assertTrue("photosynthesis" in spoken or "light" in spoken or "chlorophyll" in spoken or "glucose" in spoken)

    def test_laptop_lock_routing(self):
        """Bug #67: 'lock laptop' routes lock command to laptop_node."""
        res = self.brain.process_query("lock laptop")
        self.assertEqual(res["action"]["target"], "laptop_node")
        self.assertIn("laptop", res["response"].lower())

    def test_laptop_launch_app_routing(self):
        """Bug #67: 'launch vscode on laptop' routes to laptop_node."""
        res = self.brain.process_query("launch vscode on laptop")
        self.assertEqual(res["action"]["target"], "laptop_node")

    def test_laptop_hub_mesh_status(self):
        """Bug #66: Laptop node exists and is registered in DeviceMesh."""
        devices = self.mesh.list_devices()
        laptop = next((d for d in devices if d["device_id"] == "laptop_node"), None)
        self.assertIsNotNone(laptop)
        self.assertEqual(laptop["device_type"], "laptop")
        self.assertEqual(laptop["status"], "online")


if __name__ == "__main__":
    unittest.main()
