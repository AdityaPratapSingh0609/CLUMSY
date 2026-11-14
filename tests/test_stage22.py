"""Stage 22 Verification Suite: Deep 22-Stage End-to-End Bug Hunt, Preflight Readiness & Production Sign-Off."""

from __future__ import annotations

import unittest

from scripts.deploy_jarvis import run_preflight_checks


class TestStage22EndToEndProductionReadiness(unittest.TestCase):
    def test_all_22_stages_preflight_and_bug_fixes_pass(self) -> None:
        report = run_preflight_checks()
        self.assertTrue(report["ready_for_deploy"], f"Preflight failed: {report}")
        self.assertEqual(report["stages_verified"], 22)
        self.assertTrue(report["local_gguf_ready"])
        self.assertTrue(report["eyeball_engine_ready"])
        self.assertTrue(report["mobile_agent_ready"])
        self.assertTrue(report["laptop_job_engine_ready"])
        self.assertTrue(report["background_daemon_ready"])
        self.assertLessEqual(report["active_ram_mb"], 850)


if __name__ == "__main__":
    unittest.main()
