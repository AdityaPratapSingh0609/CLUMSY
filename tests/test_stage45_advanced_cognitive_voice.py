"""
Stage 45 Advanced Cognitive & Voice Automation Tests
Validates Bugs #133–#144:
- Bug #134: Voice & Volume Controls
- Bug #135: Explicit Chain-of-Thought (CoT) & Logic Riddles
- Bug #136: Multi-Turn Socratic Clarification
- Bug #138: Financial Math (Compound Interest, Simple Interest, Amortization)
- Bug #139: Algorithmic Refactoring
"""

import unittest
from core.llm_engine import LLMEngine


class TestStage45AdvancedCognitiveVoice(unittest.TestCase):
    def setUp(self):
        self.engine = LLMEngine(model_path=None)

    def test_voice_volume_and_rate_control(self):
        """Bug #134: Voice volume and speech rate control commands."""
        r1 = self.engine.generate("speak slower")
        self.assertEqual(r1["tool_call"]["tool"], "answer_query")
        self.assertEqual(r1["tool_call"]["params"]["topic"], "voice_settings")
        self.assertEqual(r1["tool_call"]["params"]["action"], "speed_down")

        r2 = self.engine.generate("speak faster")
        self.assertEqual(r2["tool_call"]["params"]["action"], "speed_up")

        r3 = self.engine.generate("normal speed")
        self.assertEqual(r3["tool_call"]["params"]["action"], "speed_reset")

        r4 = self.engine.generate("set volume to 80%")
        self.assertEqual(r4["tool_call"]["params"]["action"], "set_volume")
        self.assertEqual(r4["tool_call"]["params"]["volume"], 80)

        r5 = self.engine.generate("mute voice")
        self.assertEqual(r5["tool_call"]["params"]["action"], "mute")

        r6 = self.engine.generate("unmute voice")
        self.assertEqual(r6["tool_call"]["params"]["action"], "unmute")

    def test_chain_of_thought_logic_riddles(self):
        """Bug #135: Logic riddles solved step by step."""
        r1 = self.engine.generate("how to get the wolf, goat, and cabbage across the river")
        self.assertIn("Goat", r1["spoken_response"])
        self.assertIn("7 steps", r1["spoken_response"])

        r2 = self.engine.generate("should i switch doors in the monty hall problem")
        self.assertIn("switch", r2["spoken_response"].lower())
        self.assertIn("2/3", r2["spoken_response"])

        r3 = self.engine.generate("bridge and torch riddle with four people")
        self.assertIn("17 min", r3["spoken_response"])

        r4 = self.engine.generate("three mislabelled boxes of apples and oranges")
        self.assertIn("Mixed", r4["spoken_response"])

    def test_financial_math_compound_interest(self):
        """Bug #138: Deterministic Compound Interest formula A = P(1+r)^t."""
        math_res = self.engine._try_solve_math("compound interest on $1000 at 5% for 3 years")
        self.assertIsNotNone(math_res)
        self.assertIn("1,157.63", math_res)
        self.assertIn("157.63", math_res)

    def test_financial_math_simple_interest(self):
        """Bug #138: Deterministic Simple Interest formula I = Prt/100."""
        math_res = self.engine._try_solve_math("simple interest on 5000 at 4% for 2 years")
        self.assertIsNotNone(math_res)
        self.assertIn("400.00", math_res)
        self.assertIn("5,400.00", math_res)

    def test_financial_math_loan_payment(self):
        """Bug #138: Monthly loan payment / mortgage calculation."""
        math_res = self.engine._try_solve_math("monthly payment for 200000 at 6% for 30 years")
        self.assertIsNotNone(math_res)
        self.assertIn("1,199.10", math_res)

    def test_socratic_clarification_ambiguous_queries(self):
        """Bug #136: Ambiguous questions trigger Socratic clarification."""
        r1 = self.engine.generate("how much does it cost?")
        self.assertIn("Which product", r1["spoken_response"])

        r2 = self.engine.generate("who won the match?")
        self.assertIn("Which sports match", r2["spoken_response"])

        r3 = self.engine.generate("what is the formula?")
        self.assertIn("Which scientific or mathematical formula", r3["spoken_response"])

        r4 = self.engine.generate("how do i get there?")
        self.assertIn("starting location", r4["spoken_response"])

    def test_code_refactoring_algorithmic_complexity(self):
        """Bug #139: Multi-turn code refactoring."""
        r = self.engine.generate("refactor nested loop to hash map")
        self.assertIsNotNone(r["spoken_response"])

    def test_linear_equation_solver_intact(self):
        """Verify Bug #122 regression check for linear equations."""
        res = self.engine._try_solve_math("solve 3x + 5 = 20")
        self.assertIsNotNone(res)
        self.assertIn("5", res)

    def test_general_intents_intact(self):
        """Verify greetings, status, and expressions remain intact."""
        r = self.engine.generate("hello clumsy")
        self.assertEqual(r["robot_expression"], "happy")


if __name__ == "__main__":
    unittest.main()
