"""Stage 15 Verification Suite: Real Local GGUF Runtime (`llama-cpp-python` + Model Weights) & Zero-Brag J.A.R.V.I.S. Brain."""

from __future__ import annotations

import unittest

from core.llm_engine import LLMEngine
from core.llm_fusion import (
    FORBIDDEN_BRAG_PHRASES,
    MODEL_ROSTER,
    JarvisFusionModel,
    SingleSlotRAMGuard,
)
from scripts.download_model import PRIMARY_GGUF_PATH, is_valid_gguf


class TestStage15JarvisMultiModelFusion(unittest.TestCase):
    def test_01_llama_cpp_and_local_gguf_weights_present(self) -> None:
        """Verify Bug Fix #3: llama-cpp-python is installed and real GGUF weights exist in models/."""
        import llama_cpp  # type: ignore

        self.assertTrue(hasattr(llama_cpp, "Llama"))
        self.assertTrue(
            is_valid_gguf(PRIMARY_GGUF_PATH),
            f"Expected valid GGUF model at {PRIMARY_GGUF_PATH}",
        )

        engine = LLMEngine(model_path=PRIMARY_GGUF_PATH)
        self.assertEqual(engine.engine_name, "llama_cpp_gguf")
        self.assertIsNotNone(engine.llm)
        raw_out = engine.generate_raw_completion(
            "Say hello in one short sentence.",
            system_prompt="You are J.A.R.V.I.S.",
            max_tokens=24,
        )
        self.assertTrue(isinstance(raw_out, str) and len(raw_out.strip()) > 0)

    def test_02_four_model_roster_and_ultra_low_ram_single_slot_guard(self) -> None:
        self.assertEqual(set(MODEL_ROSTER.keys()), {"qwen3.5", "gemma4", "llama4", "mistral"})

        guard = SingleSlotRAMGuard(max_ram_mb=850)
        for mod_id in ("qwen3.5", "gemma4", "llama4", "mistral"):
            eng = guard.acquire_specialist(mod_id)
            self.assertIsNotNone(eng)
            self.assertEqual(guard.active_slot, mod_id)
            self.assertLessEqual(guard.current_ram_mb, 850)
        self.assertEqual(guard.swap_count, 4)

    def test_03_zero_model_bragging_and_authentic_jarvis_persona(self) -> None:
        """Verify Bug Fix #2: No response ever contains robotic model-bragging text."""
        fusion = JarvisFusionModel(max_ram_mb=850)

        prompts = [
            "write a java code to print my name is aditya pratap singh",
            "give me a java code to print my name is aditya pratap singh",
            "make a ppt on AI",
            "draw a graphic logo for deskbot",
            "hello jarvis, how are you?",
        ]
        for p in prompts:
            res = fusion.generate(p)
            spoken_low = res["spoken_response"].lower()
            for brag in FORBIDDEN_BRAG_PHRASES:
                self.assertNotIn(
                    brag,
                    spoken_low,
                    f"Forbidden model brag '{brag}' found in reply to '{p}': {res['spoken_response']}",
                )
            self.assertNotIn("i heard:", spoken_low)

    def test_04_specialist_routing_and_java_code_intent(self) -> None:
        fusion = JarvisFusionModel(max_ram_mb=850)

        # 1. Java coding query -> Qwen 3.5 leads + language='java'
        java_res = fusion.generate("write a java code to print my name is aditya pratap singh")
        self.assertEqual(java_res["fusion"]["lead_specialist"], "qwen3.5")
        self.assertEqual(java_res["tool_call"]["tool"], "job_executor")
        self.assertEqual(java_res["tool_call"]["params"]["job_type"], "code")
        self.assertEqual(java_res["tool_call"]["params"]["language"], "java")
        self.assertLessEqual(java_res["fusion"]["active_ram_mb"], 850)

        # 2. Creative explanation query -> Gemma 4 leads
        gemma_res = fusion.generate("Explain why black holes warp spacetime and write a summary")
        self.assertEqual(gemma_res["fusion"]["lead_specialist"], "gemma4")

        # 3. System / Mesh query -> Llama 4 leads
        llama_res = fusion.generate("Open Spotify on my laptop and check phone battery")
        self.assertEqual(llama_res["fusion"]["lead_specialist"], "llama4")

        # 4. Executive status briefing -> Mistral leads
        mistral_res = fusion.generate("Hello Jarvis, give me a fast status overview")
        self.assertEqual(mistral_res["fusion"]["lead_specialist"], "mistral")

        # Weights always sum to 1.0
        self.assertAlmostEqual(sum(mistral_res["fusion"]["weights"].values()), 1.0, places=2)

    def test_05_multi_turn_conversation_memory(self) -> None:
        fusion = JarvisFusionModel(max_ram_mb=850)
        fusion.generate("Hello Jarvis, my name is Aditya Pratap Singh")
        self.assertGreaterEqual(len(fusion.history), 2)
        recall = fusion.generate("What is my name?")
        self.assertIn("Aditya Pratap Singh", recall["spoken_response"])


if __name__ == "__main__":
    unittest.main()
