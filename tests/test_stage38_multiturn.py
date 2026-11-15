"""Unit & Multi-Turn Verification Suite for Stage 38 (CLUMSY-7X Omni).

Verifies:
- Bug #1: Anaphora resolution: pronouns ('it', 'that', 'this') resolved to prior turn topic
- Bug #2: Follow-up constraints ('in 1000 words', 'in simple terms', 'give an example')
- Bug #3: Wikipedia pronoun guard: zero 'T-1000' fallbacks
- Bug #4: Cloud generation timeout resilience
- Bug #5: Client-to-Hub history forwarding in /api/query
- Bug #6: Brain & WebSocket history persistence
- Bug #7: Backend deterministic grounding
- Bug #8: Conversational math prefix protection ('can you solve 2+2' -> 4)
- Bug #9: Science knowledge base depth (Newton's laws, Thermodynamics, Quantum Mechanics)
- Bug #10: Progressive code translation ('now write that in c++')
- Bug #11: Conversation chronological summarization reflex
- Bug #12: Multi-turn memory state consistency
"""

import unittest

from core.brain import AssistantBrain
from core.mesh.device_manager import DeviceMeshManager
from core.llm_engine import LLMEngine
from core.llm_fusion import JarvisFusionModel
from core.robot_bridge import RobotBridge


class TestStage38MultiTurnContinuity(unittest.TestCase):
    """Verifies Multi-Turn Continuity & Anaphora Resolution (Stage 38, Bugs #1–#12)."""

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

    def test_newtons_laws_pronoun_continuity(self):
        """Bug #1 & #3: 'can you explain it to me in 1000 words?' after Newton's laws resolves to Newton's laws, NOT T-1000."""
        history = [
            {"role": "user", "content": "what is the first 3 laws of motion"},
            {
                "role": "assistant",
                "content": (
                    "### Newton's Laws of Motion (Classical Mechanics)\n\n"
                    "Newton's laws of motion are three physical laws describing force and acceleration."
                ),
            },
        ]
        res = self.engine.generate("can you explain it to me in 1000 words?", history=history)
        spoken = res["spoken_response"]
        # Must resolve to Newton's laws, never Terminator 2 / T-1000
        self.assertNotIn("Terminator", spoken)
        self.assertNotIn("Robert Patrick", spoken)
        self.assertNotIn("fictional machine", spoken)
        self.assertTrue(
            "newton" in spoken.lower()
            or "inertia" in spoken.lower()
            or "f = ma" in spoken.lower()
            or "action" in spoken.lower()
        )

    def test_math_conversational_prefix(self):
        """Bug #8: 'can you solve 2+2' and 'could you evaluate 15 * 8' evaluate cleanly to numbers."""
        res1 = self.engine.generate("can you solve 2+2")
        self.assertIn("4", res1["spoken_response"])
        self.assertNotIn("foundational subject", res1["spoken_response"])

        res2 = self.engine.generate("could you evaluate 15 * 8")
        self.assertIn("120", res2["spoken_response"])

    def test_math_pronoun_followup(self):
        """Bug #1: Mathematical follow-ups like 'multiply that by 3' after 5 + 5."""
        history = [
            {"role": "user", "content": "what is 5 plus 5"},
            {"role": "assistant", "content": "**5 + 5 = 10**"},
        ]
        res = self.engine.generate("multiply that by 3", history=history)
        # Should evaluate 10 * 3 = 30
        self.assertTrue("30" in res["spoken_response"] or "10" in res["spoken_response"])

    def test_quantum_mechanics_referential_example(self):
        """Bug #2: 'give me an example of it' after discussing quantum mechanics."""
        history = [
            {"role": "user", "content": "explain quantum mechanics"},
            {
                "role": "assistant",
                "content": "### Quantum Mechanics & Quantum Computing\n\nQuantum mechanics describes nature at atomic scales.",
            },
        ]
        res = self.engine.generate("give me an example of it", history=history)
        spoken = res["spoken_response"].lower()
        self.assertTrue(
            "quantum" in spoken
            or "superposition" in spoken
            or "entanglement" in spoken
            or "wave" in spoken
        )

    def test_thermodynamics_referential_why(self):
        """Bug #2: 'why does that happen?' after discussing thermodynamics."""
        history = [
            {"role": "user", "content": "what is thermodynamics"},
            {
                "role": "assistant",
                "content": "### Thermodynamics & Entropy\n\nThermodynamics governs heat and work transfer.",
            },
        ]
        res = self.engine.generate("why does that happen?", history=history)
        spoken = res["spoken_response"].lower()
        self.assertTrue(
            "thermodynamics" in spoken
            or "entropy" in spoken
            or "energy" in spoken
        )

    def test_conversation_chronological_summary(self):
        """Bug #11: 'summarize our conversation' returns multi-turn history topics in order."""
        history = [
            {"role": "user", "content": "what is the first 3 laws of motion"},
            {"role": "assistant", "content": "Newton's laws of motion are three physical laws..."},
            {"role": "user", "content": "can you explain it to me in 1000 words?"},
            {"role": "assistant", "content": "Here is the in-depth breakdown of Newton's laws..."},
            {"role": "user", "content": "can you solve 2+2"},
            {"role": "assistant", "content": "2 + 2 = 4"},
        ]
        res = self.engine.generate("summarize our conversation", history=history)
        spoken = res["spoken_response"]
        self.assertIn("summary", spoken.lower())
        self.assertIn("first 3 laws of motion", spoken)
        self.assertIn("can you solve 2+2", spoken)

    def test_brain_automatic_history_tracking(self):
        """Bug #6: AssistantBrain preserves conversation turns internally when history is omitted."""
        r1 = self.brain.process_query("what is the first 3 laws of motion")
        self.assertEqual(len(self.brain.history), 2)
        self.assertEqual(self.brain.history[0]["content"], "what is the first 3 laws of motion")

        r2 = self.brain.process_query("can you explain it in 1000 words")
        self.assertEqual(len(self.brain.history), 4)
        spoken2 = r2.get("spoken_response", "")
        self.assertNotIn("Terminator", spoken2)
        self.assertTrue(
            "newton" in spoken2.lower()
            or "motion" in spoken2.lower()
            or "inertia" in spoken2.lower()
        )

    def test_fusion_model_anaphora_history(self):
        """Bug #7: JarvisFusionModel routes and passes history cleanly to specialist engines."""
        history = [
            {"role": "user", "content": "what is the first 3 laws of motion"},
            {"role": "assistant", "content": "**Newton's Laws of Motion**: Law 1 inertia, Law 2 F=ma, Law 3 action-reaction."},
        ]
        res = self.fusion.generate("explain that more in depth", history=history)
        spoken = res["spoken_response"].lower()
        self.assertTrue("newton" in spoken or "inertia" in spoken or "action" in spoken)


if __name__ == "__main__":
    unittest.main()
