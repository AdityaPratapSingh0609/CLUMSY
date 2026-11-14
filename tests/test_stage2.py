import json
import unittest

from core.brain import AssistantBrain
from core.llm_engine import (
    LLMEngine,
    LLMValidationError,
    clamp_angle,
    extract_json_object,
    format_chatml_prompt,
    validate_and_normalize_response,
)
from core.mesh.device_manager import DeviceMeshManager
from core.orchestrator import Orchestrator
from core.robot_bridge import RobotBridge


class Stage2LLMTests(unittest.TestCase):
    def test_chatml_prompt_template(self):
        prompt = format_chatml_prompt("check my phone")
        self.assertIn("<|im_start|>system", prompt)
        self.assertIn("<|im_start|>user\ncheck my phone<|im_end|>", prompt)
        self.assertTrue(prompt.endswith("<|im_start|>assistant\n"))

    def test_extract_json_from_markdown_and_chatter(self):
        wrapped = 'Sure! Here is the JSON:\n```json\n{"thought": "ok", "tool_call": {"tool": "phone_check", "params": {}}, "robot_expression": "happy", "robot_servo": {"pan": 90, "tilt": 95}, "spoken_response": "Done"}\n```'
        obj = extract_json_object(wrapped)
        self.assertEqual(obj["tool_call"]["tool"], "phone_check")

    def test_schema_validation_clamps_servo_angles(self):
        raw = {
            "thought": "test clamp",
            "tool_call": {"tool": "robot_gesture", "params": {}},
            "robot_expression": "happy",
            "robot_servo": {"pan": 250, "tilt": -20},
            "spoken_response": "Clamped!",
        }
        norm = validate_and_normalize_response(raw)
        self.assertEqual(norm["robot_servo"], {"pan": 165, "tilt": 15})

    def test_schema_rejects_unknown_tool(self):
        raw = {
            "thought": "bad tool",
            "tool_call": {"tool": "delete_everything", "params": {}},
            "robot_expression": "happy",
            "robot_servo": {"pan": 90, "tilt": 90},
            "spoken_response": "Oops",
        }
        with self.assertRaises(LLMValidationError):
            validate_and_normalize_response(raw)

    def test_custom_backend_inference_and_throughput(self):
        def fake_gguf(prompt: str):
            payload = {
                "thought": "Launching VS Code on laptop",
                "tool_call": {"tool": "launch_app", "params": {"target": "laptop_node", "app_name": "VS Code"}},
                "robot_expression": "happy",
                "robot_servo": {"pan": 85, "tilt": 100},
                "spoken_response": "Opening VS Code on your laptop.",
            }
            return json.dumps(payload), 42

        engine = LLMEngine(backend=fake_gguf)
        res = engine.generate("open vscode on my laptop")
        self.assertEqual(res["engine"], "custom_backend")
        self.assertEqual(res["tool_call"]["tool"], "launch_app")
        self.assertGreaterEqual(res["tokens_per_sec"], 25.0)

    def test_brain_routes_phone_and_laptop_commands(self):
        robot = RobotBridge(simulate=True)
        robot.connect()
        mesh = DeviceMeshManager()
        brain = AssistantBrain(robot_bridge=robot, mesh_manager=mesh)

        phone_out = brain.process_query("Hey Deskbot, check my phone battery")
        self.assertEqual(phone_out["action"]["tool"], "phone_check")
        self.assertIn("87%", phone_out["response"])

        laptop_out = brain.process_query("Open Spotify on my laptop")
        self.assertEqual(laptop_out["action"]["tool"], "launch_app")
        self.assertIn("Spotify", laptop_out["response"])


class Stage2OrchestratorAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_orchestrator_end_to_end_event_flow(self):
        orch = Orchestrator()
        await orch.start()
        res = await orch.submit_query("Open VS Code on my laptop")
        self.assertEqual(res["action"]["tool"], "launch_app")
        self.assertIn("VS Code", res["response"])
        await orch.stop()


if __name__ == "__main__":
    unittest.main()
