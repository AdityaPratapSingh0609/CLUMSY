"""Stage 17 Verification Suite: Real Multi-Language Code Generator, Compiler & Live Runner (`Java`, `Python`, `C++`, `C`, `JS`, `HTML`)."""

from __future__ import annotations

from pathlib import Path
import unittest

from core.brain import AssistantBrain
from core.job_engine import UniversalJobEngine, detect_code_language, extract_print_message
from core.mesh.device_manager import DeviceMeshManager
from core.robot_bridge import RobotBridge


class TestStage17MultiLanguageCodeEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = UniversalJobEngine()

    def test_01_screenshot_bug_fix_java_print_aditya_pratap_singh(self) -> None:
        """Verify Bug Fix #1: Asking for Java code to print 'my name is aditya pratap singh' outputs real Java code."""
        for prompt in (
            "write a java code to print my name is aditya pratap singh",
            "give me a java code to print my name is aditya pratap singh",
        ):
            self.assertEqual(detect_code_language(prompt), "java")
            self.assertEqual(extract_print_message(prompt), "My name is Aditya Pratap Singh")

            artifact = self.engine.execute_job(prompt, job_type="code")
            self.assertEqual(artifact["language"], "java")
            self.assertTrue(artifact["file_path"].endswith(".java"))
            self.assertIn("public class Main", artifact["content"])
            self.assertIn("public static void main(String[] args)", artifact["content"])
            self.assertIn('System.out.println("My name is Aditya Pratap Singh");', artifact["content"])
            self.assertNotIn("def execute_jarvis_task", artifact["content"])
            self.assertEqual(artifact["stdout"], "My name is Aditya Pratap Singh")

    def test_02_brain_returns_code_in_chat_bubble_and_studio_artifact(self) -> None:
        """Verify Bug Fix #1: AssistantBrain returns the formatted code block inside the chat response AND job_artifact."""
        robot = RobotBridge(simulate=True)
        robot.connect()
        mesh = DeviceMeshManager()
        brain = AssistantBrain(robot_bridge=robot, mesh_manager=mesh, job_engine=self.engine)

        res = brain.process_query("write a java code to print my name is aditya pratap singh")
        self.assertIn("```java", res["response"])
        self.assertIn('System.out.println("My name is Aditya Pratap Singh");', res["response"])
        self.assertIn("STDOUT: My name is Aditya Pratap Singh", res["response"])
        self.assertNotIn("Qwen 3.5 and Mistral synthesized", res["response"])
        self.assertIsNotNone(res["job_artifact"])
        self.assertEqual(res["job_artifact"]["language"], "java")
        self.assertEqual(res["robot_state"], "coding")

    def test_03_multi_language_synthesis_and_real_execution(self) -> None:
        # 1. Python Fibonacci (runs via real Python interpreter)
        py_art = self.engine.execute_job("Write python code for fibonacci", job_type="code")
        self.assertEqual(py_art["language"], "python")
        self.assertTrue(Path(py_art["file_path"]).is_file())
        self.assertIn("Fibonacci(10): [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]", py_art["stdout"])

        # 2. C++ Print
        cpp_art = self.engine.execute_job("Write a C++ program to print Hello Stark Tower", job_type="code")
        self.assertEqual(cpp_art["language"], "cpp")
        self.assertIn("#include <iostream>", cpp_art["content"])
        self.assertEqual(cpp_art["stdout"], "Hello Stark Tower")

        # 3. JavaScript (runs via Node.js if present)
        js_art = self.engine.execute_job("Write javascript code to sort an array", job_type="code")
        self.assertEqual(js_art["language"], "javascript")
        self.assertIn("[4,8,15,16,23,42,99]", js_art["stdout"].replace(" ", ""))

        # 4. Java Factorial & Prime
        java_fact = self.engine.execute_job("Write a java program for factorial of 6", job_type="code")
        self.assertEqual(java_fact["language"], "java")
        self.assertEqual(java_fact["stdout"], "Factorial(6) = 720")


if __name__ == "__main__":
    unittest.main()
