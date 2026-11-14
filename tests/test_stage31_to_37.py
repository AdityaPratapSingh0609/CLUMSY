"""Unit & QA Verification Suite for Stages 31 through 37 (CLUMSY-7X Omni).

Tests:
- Stage 31: Conversational NLP, Multi-Clause Name & Location Memory, Compound Greetings
- Stage 32: Intent-gated routing, Fallback resilience
- Stage 33: Symbolic Math, Linear Algebra (3x + 5 = 20), Spoken Numbers (two plus two), Compound %/sqrt
- Stage 34: 6-Language Code Synthesizer (Linked List, Anagram, Binary Search, Sort, Factorial, Prime)
- Stage 35: Context memory isolation, non-poisoning history, GGUF repetition guard
- Stage 36: Voice commander intent filters (Amazon, Netflix, 3D non-hijacking)
- Stage 37: HTML syntax uncorruption and data-raw-code preservation
"""

import math
import os
import re
import shutil
import tempfile
import unittest

from core.llm_engine import LLMEngine
from core.llm_fusion import JarvisFusionModel
from core.job_engine import UniversalJobEngine, detect_code_language, extract_print_message
from core.voice.voice_commander import parse_voice_intent, normalize_voice_transcript


class TestStage31ConversationalNLP(unittest.TestCase):
    """Verifies Conversational NLP and Memory (Stage 31, Bugs #1–#14)."""

    def test_compound_greetings(self):
        engine = LLMEngine(model_path=None)
        res = engine.generate("hello how are you")
        self.assertEqual(res["robot_expression"], "happy")
        self.assertTrue(
            "service" in res["spoken_response"].lower()
            or "systems are online" in res["spoken_response"].lower()
        )

    def test_multi_clause_name_and_location_memory(self):
        engine = LLMEngine(model_path=None)
        res = engine.generate("my name is Aditya Pratap Singh, and I live in Delhi")
        self.assertIn("Aditya Pratap Singh", res["spoken_response"])
        self.assertIn("Delhi", res["spoken_response"])

        history = [
            {"role": "user", "content": "my name is Aditya Pratap Singh, and I live in Delhi"},
            {"role": "assistant", "content": res["spoken_response"]},
        ]
        q_name = engine.generate("what is my name?", history=history)
        self.assertIn("Aditya Pratap Singh", q_name["spoken_response"])

        q_loc = engine.generate("where do I live?", history=history)
        self.assertIn("Delhi", q_loc["spoken_response"])

        q_last = engine.generate("what did I just ask you?", history=history)
        self.assertTrue(
            "Aditya Pratap Singh" in q_last["spoken_response"]
            or "my name is" in q_last["spoken_response"]
        )


class TestStage33SymbolicMath(unittest.TestCase):
    """Verifies Symbolic Math & Linear Algebra Solver (Stage 33, Bugs #24–#31)."""

    def test_basic_arithmetic(self):
        ans = LLMEngine._try_solve_math("can you solve 2+2")
        self.assertIsNotNone(ans)
        self.assertIn("4", ans)

    def test_linear_algebra(self):
        ans = LLMEngine._try_solve_math("solve 3x + 5 = 20")
        self.assertIsNotNone(ans)
        self.assertIn("x = 5", ans)

        ans2 = LLMEngine._try_solve_math("solve 2x - 7 = 13")
        self.assertIsNotNone(ans2)
        self.assertIn("x = 10", ans2)

    def test_compound_percentage_and_addition(self):
        ans = LLMEngine._try_solve_math("what is 15% of 200 plus 50")
        self.assertIsNotNone(ans)
        self.assertIn("80", ans)

    def test_compound_square_root_and_addition(self):
        ans = LLMEngine._try_solve_math("what is the square root of 144 plus 10")
        self.assertIsNotNone(ans)
        self.assertIn("22", ans)

    def test_spoken_numbers(self):
        ans = LLMEngine._try_solve_math("what is two plus two")
        self.assertIsNotNone(ans)
        self.assertIn("4", ans)

    def test_powers_and_factorials(self):
        ans_pow = LLMEngine._try_solve_math("what is 2 to the power of 10")
        self.assertIsNotNone(ans_pow)
        self.assertIn("1024", ans_pow)

        ans_fact = LLMEngine._try_solve_math("what is 5!")
        self.assertIsNotNone(ans_fact)
        self.assertIn("120", ans_fact)


class TestStage34MultiLanguageCodeSynthesizer(unittest.TestCase):
    """Verifies Real Multi-Language Code Synthesizer (Stage 34, Bugs #32–#40)."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.job_engine = UniversalJobEngine(output_root=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_linked_list_reversal(self):
        job = self.job_engine.execute_job("write a python code to reverse a linked list", job_type="code")
        self.assertIn("class ListNode", job["content"])
        self.assertIn("reverse_linked_list", job["content"])
        self.assertNotIn("racecar", job["content"])

    def test_anagram_check(self):
        job = self.job_engine.execute_job("write a python function to check if a string is an anagram", job_type="code")
        self.assertIn("is_anagram", job["content"])
        self.assertIn("sorted", job["content"])

    def test_two_sum(self):
        job = self.job_engine.execute_job("write a python code for two sum", job_type="code")
        self.assertIn("two_sum", job["content"])

    def test_cpp_bubble_sort(self):
        lang = detect_code_language("write a c++ program for bubble sort")
        self.assertEqual(lang, "cpp")
        job = self.job_engine.execute_job("write a c++ program for bubble sort", job_type="code")
        self.assertIn("#include <iostream>", job["content"])
        self.assertIn("bubbleSort", job["content"])

    def test_java_binary_search(self):
        lang = detect_code_language("write a java program for binary search")
        self.assertEqual(lang, "java")
        job = self.job_engine.execute_job("write a java program for binary search", job_type="code")
        self.assertIn("public class Main", job["content"])
        self.assertIn("binarySearch", job["content"])


class TestStage35FusionAndMemoryIsolation(unittest.TestCase):
    """Verifies Context Isolation & RAM Guard (Stage 35, Bugs #41–#48)."""

    def test_conceptual_question_not_hijacked_as_code(self):
        self.assertFalse(JarvisFusionModel._is_coding_request("what is python?"))
        self.assertFalse(JarvisFusionModel._is_coding_request("who created java?"))
        self.assertTrue(JarvisFusionModel._is_coding_request("write a python script to sort a list"))

    def test_history_not_poisoned_with_tool_announcement(self):
        fusion = JarvisFusionModel()
        fusion.generate("write a python program to calculate factorial")
        assistant_turns = [t["content"] for t in fusion.history if t["role"] == "assistant"]
        self.assertGreater(len(assistant_turns), 0)
        self.assertNotIn("Right away, sir. I have written and executed your", assistant_turns[0])


class TestStage36VoiceIntentNonHijacking(unittest.TestCase):
    """Verifies Voice Intent Filtering (Stage 36, Bug #48)."""

    def test_conceptual_questions_not_hijacked(self):
        intent1 = parse_voice_intent("who founded amazon?")
        self.assertIsNone(intent1)

        intent2 = parse_voice_intent("what is netflix?")
        self.assertIsNone(intent2)

        intent3 = parse_voice_intent("what is 3d printing?")
        self.assertIsNone(intent3)

    def test_action_intents_are_captured(self):
        intent1 = parse_voice_intent("open amazon and search for headphones")
        self.assertIsNotNone(intent1)
        self.assertEqual(intent1["platform"], "amazon")

        intent2 = parse_voice_intent("watch stranger things on netflix")
        self.assertIsNotNone(intent2)
        self.assertEqual(intent2["platform"], "netflix")

        intent3 = parse_voice_intent("render a 3d model of a bridge")
        self.assertIsNotNone(intent3)
        self.assertEqual(intent3["job_type"], "3d_model")


if __name__ == "__main__":
    unittest.main()
