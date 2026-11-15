"""Tests for Stage 41: Advanced Cognitive Chain-of-Thought, Counterfactual & Comparison Engine.

Covers:
- Bug #85: Multi-Step Chain-of-Thought Deductions
- Bug #86: Counterfactual & Hypothetical Reasoning ("What if...")
- Bug #87: Logical Fallacy Detector & Refutations
- Bug #88: Foundational Thought Experiments & Paradoxes
- Bug #89: Direct Technology Comparison Matrix
"""

from __future__ import annotations

import unittest
from core.llm_engine import LLMEngine


class TestStage41CognitiveReasoning(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.llm = LLMEngine()

    def test_chain_of_thought_compiler(self) -> None:
        """Bug #85: Chain-of-Thought on how a compiler works."""
        res = self.llm._deterministic_intent("explain step by step how does a compiler work")
        resp = res["spoken_response"]
        self.assertIn("Chain-of-Thought", resp)
        self.assertTrue("Lexical" in resp or "AST" in resp or "Optimization" in resp)

    def test_chain_of_thought_ice_floating(self) -> None:
        """Bug #85: Chain-of-Thought on why ice floats on water."""
        res = self.llm._deterministic_intent("why does ice float on water")
        resp = res["spoken_response"]
        self.assertTrue("density" in resp.lower() or "hexagonal" in resp.lower() or "buoyant" in resp.lower())

    def test_counterfactual_gravity_doubled(self) -> None:
        """Bug #86: Counterfactual reasoning on doubled Earth gravity."""
        res = self.llm._deterministic_intent("what if gravity were doubled on Earth")
        resp = res["spoken_response"]
        self.assertIn("Counterfactual Analysis", resp)
        self.assertTrue("weight" in resp.lower() or "atmospheric" in resp.lower() or "gravity" in resp.lower())

    def test_counterfactual_moon_disappeared(self) -> None:
        """Bug #86: Counterfactual reasoning on Moon disappearing."""
        res = self.llm._deterministic_intent("what if the Moon disappeared instantly")
        resp = res["spoken_response"]
        self.assertIn("Counterfactual Analysis", resp)
        self.assertTrue("tidal" in resp.lower() or "axial" in resp.lower() or "tides" in resp.lower())

    def test_thought_experiment_schrodinger(self) -> None:
        """Bug #88: Thought experiment - Schrödinger's Cat."""
        res = self.llm._deterministic_intent("explain schrodinger's cat thought experiment")
        resp = res["spoken_response"]
        self.assertTrue("Schrödinger" in resp or "superposition" in resp.lower() or "decoherence" in resp.lower())

    def test_thought_experiment_trolley_problem(self) -> None:
        """Bug #88: Thought experiment - The Trolley Problem."""
        res = self.llm._deterministic_intent("what is the trolley problem")
        resp = res["spoken_response"]
        self.assertTrue("Trolley" in resp or "utilitarianism" in resp.lower() or "ethics" in resp.lower())

    def test_logical_fallacy_ad_hominem(self) -> None:
        """Bug #87: Logical Fallacy - Ad Hominem."""
        res = self.llm._deterministic_intent("what fallacy is this: you are too young to understand economics")
        resp = res["spoken_response"]
        self.assertIn("Ad Hominem", resp)

    def test_logical_fallacy_slippery_slope(self) -> None:
        """Bug #87: Logical Fallacy - Slippery Slope."""
        res = self.llm._deterministic_intent("what fallacy: if we allow calculators nobody will ever learn math again")
        resp = res["spoken_response"]
        self.assertIn("Slippery Slope", resp)

    def test_comparison_python_vs_cpp(self) -> None:
        """Bug #89: Direct Comparison - Python vs C++."""
        res = self.llm._deterministic_intent("Python vs C++")
        resp = res["spoken_response"]
        self.assertTrue("Python" in resp and "C++" in resp)
        self.assertTrue("Interpreted" in resp or "Native" in resp or "Compiled" in resp)

    def test_comparison_tcp_vs_udp(self) -> None:
        """Bug #89: Direct Comparison - TCP vs UDP."""
        res = self.llm._deterministic_intent("TCP vs UDP")
        resp = res["spoken_response"]
        self.assertTrue("TCP" in resp and "UDP" in resp)
        self.assertTrue("Connection" in resp or "Reliable" in resp or "latency" in resp.lower())


if __name__ == "__main__":
    unittest.main()
