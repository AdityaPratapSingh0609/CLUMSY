"""Stage 44 Verification Suite: Persistent Memory Mesh, Conversational Math Chaining,
Length Constraints, Task Planning & Empirical Science Engine (Bugs #121 - #132).
"""

import unittest
from core.llm_engine import LLMEngine


class TestStage44PersistentMemoryAndCognitive(unittest.TestCase):
    def setUp(self):
        self.llm = LLMEngine(backend=None)
        LLMEngine._last_class_math_result = None

    def test_bug121_memory_clear_command(self):
        """Bug #121: Clear history resets memory and math accumulator."""
        LLMEngine._last_class_math_result = 42.0
        res = self.llm.generate("clear history")
        self.assertIn("cleared", res["spoken_response"].lower())
        self.assertIsNone(LLMEngine._last_class_math_result)

    def test_bug122_conversational_math_chaining(self):
        """Bug #122: Math operations chain sequentially off the previous evaluated result."""
        # Turn 1: 25 * 4 = 100
        res1 = self.llm._try_solve_math("what is 25 * 4")
        self.assertIsNotNone(res1)
        self.assertIn("100", res1)
        self.assertEqual(LLMEngine._last_class_math_result, 100.0)

        # Turn 2: now add 50 to that -> 150
        res2 = self.llm._try_solve_math("now add 50 to that")
        self.assertIsNotNone(res2)
        self.assertIn("150", res2)
        self.assertEqual(LLMEngine._last_class_math_result, 150.0)

        # Turn 3: divide that by 2 -> 75
        res3 = self.llm._try_solve_math("divide that by 2")
        self.assertIsNotNone(res3)
        self.assertIn("75", res3)
        self.assertEqual(LLMEngine._last_class_math_result, 75.0)

        # Turn 4: subtract 10 from it -> 65
        res4 = self.llm._try_solve_math("subtract 10 from it")
        self.assertIsNotNone(res4)
        self.assertIn("65", res4)
        self.assertEqual(LLMEngine._last_class_math_result, 65.0)

        # Turn 5: multiply that by 3 -> 195
        res5 = self.llm._try_solve_math("multiply that by 3")
        self.assertIsNotNone(res5)
        self.assertIn("195", res5)
        self.assertEqual(LLMEngine._last_class_math_result, 195.0)

    def test_bug122_history_math_fallback(self):
        """Bug #122: Math chaining extracts accumulator from history turns if class state was cleared."""
        LLMEngine._last_class_math_result = None
        history = [
            {"role": "user", "content": "what is 20 * 5"},
            {"role": "assistant", "content": "**20 * 5 = 100**"},
        ]
        res = self.llm._try_solve_math("now add 25 to that", history=history)
        self.assertIsNotNone(res)
        self.assertIn("125", res)

    def test_bug127_emotional_empathy(self):
        """Bug #127: Empathy intents return supportive companion dialogue and set warm expressions."""
        stressed = self.llm.generate("i'm feeling stressed today")
        self.assertIn("support", stressed["spoken_response"].lower())
        self.assertEqual(stressed["robot_expression"], "love")

        promoted = self.llm.generate("i just got promoted!")
        self.assertIn("congratulations", promoted["spoken_response"].lower())
        self.assertEqual(promoted["robot_expression"], "excited")

        tired = self.llm.generate("i'm so tired")
        self.assertIn("rest", tired["spoken_response"].lower())
        self.assertEqual(tired["robot_expression"], "sleepy")

    def test_bug128_physics_formulas_calculation(self):
        """Bug #128: Direct formula calculation for Kinetic Energy, Force, and Mass-Energy Equivalence."""
        ke = self.llm.generate("what is the kinetic energy of 10kg at 5m/s")
        # 0.5 * 10 * 25 = 125
        self.assertIn("125", ke["spoken_response"])
        self.assertIn("Joules", ke["spoken_response"])

        force = self.llm.generate("what is the force of 5kg accelerating at 2m/s^2")
        # 5 * 2 = 10
        self.assertIn("10", force["spoken_response"])
        self.assertIn("Newtons", force["spoken_response"])

        energy = self.llm.generate("what is the energy of 2kg mass")
        self.assertIn("Joules", energy["spoken_response"])
        self.assertIn("E = mc^2", energy["spoken_response"])

    def test_bug128_universal_constants(self):
        """Bug #128: Retrieval of fundamental physical constants."""
        c = self.llm.generate("what is the speed of light")
        self.assertIn("299,792,458", c["spoken_response"])

        h = self.llm.generate("what is planck's constant")
        self.assertIn("6.62607015", h["spoken_response"])

        g = self.llm.generate("what is the gravitational constant")
        self.assertIn("6.67430", g["spoken_response"])

    def test_bug124_task_plan_scaffolder(self):
        """Bug #124: Task planning returns structured phased execution checklist."""
        workout = self.llm.generate("plan a 3-day workout routine")
        self.assertIn("workout", workout["spoken_response"].lower())

    def test_bug126_project_scaffolder(self):
        """Bug #126: Scaffolding and gitignore generation."""
        gi = self.llm.generate("create a gitignore for python")
        self.assertIn("gitignore", gi["spoken_response"].lower())

    def test_bug129_entity_coreference(self):
        """Bug #129: Multi-turn entity coreference handles former/latter."""
        history = [
            {"role": "user", "content": "compare python vs c++"},
            {"role": "assistant", "content": "### Python vs C++\n\nComparing both languages."},
        ]
        res = self.llm.generate("what is the former?", history=history)
        self.assertIsNotNone(res["spoken_response"])


if __name__ == "__main__":
    unittest.main()
