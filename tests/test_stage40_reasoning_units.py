"""
Stage 40 Unit Tests: Multi-Step Cognitive Reasoning, Unit Conversions, Financial Math, Word Problems & Silence Barge-In.
"""

import unittest
from core.llm_engine import LLMEngine
from core.brain import AssistantBrain


class TestStage40ReasoningUnits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.llm = LLMEngine()

    def test_unit_conversion_km_to_miles(self):
        """Bug #74: Convert 10 km to miles."""
        res = self.llm._try_solve_math("convert 10 km to miles")
        self.assertIsNotNone(res)
        self.assertIn("6.2137", res)

    def test_unit_conversion_miles_to_km(self):
        """Bug #74: Convert 10 miles to km."""
        res = self.llm._try_solve_math("convert 10 miles to km")
        self.assertIsNotNone(res)
        self.assertIn("16.0934", res)

    def test_unit_conversion_celsius_to_fahrenheit(self):
        """Bug #74: Convert 25 celsius to fahrenheit."""
        res = self.llm._try_solve_math("convert 25 celsius to fahrenheit")
        self.assertIsNotNone(res)
        self.assertIn("77", res)

    def test_unit_conversion_meters_to_feet(self):
        """Bug #74: Convert 6 meters to feet."""
        res = self.llm._try_solve_math("convert 6 meters to feet")
        self.assertIsNotNone(res)
        self.assertIn("19.685", res)

    def test_financial_math_discount(self):
        """Bug #75: 20% discount on $150."""
        res = self.llm._try_solve_math("20% discount on 150 dollars")
        self.assertIsNotNone(res)
        self.assertIn("120", res)
        self.assertIn("30", res)

    def test_financial_math_tip(self):
        """Bug #75: 15% tip on 85 dollars."""
        res = self.llm._try_solve_math("15% tip on 85 dollars")
        self.assertIsNotNone(res)
        self.assertIn("12.75", res)
        self.assertIn("97.75", res)

    def test_word_problem_speed_distance(self):
        """Bug #73: Car traveling 60 mph for 3.5 hours."""
        res = self.llm._try_solve_math("A car travels 60 mph for 3.5 hours, how far does it travel?")
        self.assertIsNotNone(res)
        self.assertIn("210", res)

    def test_word_problem_inventory_subtraction(self):
        """Bug #73: Alice has 15 apples and gives 4 to Bob and 3 to Charlie."""
        res = self.llm._try_solve_math("Alice has 15 apples and gives 4 to Bob and 3 to Charlie, how many does she have left?")
        self.assertIsNotNone(res)
        self.assertIn("8", res)

    def test_speech_silence_command(self):
        """Bug #78: 'stop talking' triggers silence intent."""
        intent = self.llm._deterministic_intent("stop talking")
        self.assertEqual(intent["tool_call"]["tool"], "answer_query")
        self.assertEqual(intent["tool_call"]["params"]["topic"], "silence")
        self.assertIn("silenced", intent["spoken_response"].lower())


if __name__ == "__main__":
    unittest.main()
