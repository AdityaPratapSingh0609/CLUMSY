"""Tests for Stage 42: Developer & Technical Tool Synthesizer, Regex, SQL, Git & STEM Problem Solver.
Fixes Bugs #97 - #108.
"""

from __future__ import annotations

import unittest
from core.llm_engine import LLMEngine


class TestStage42DeveloperTechnicalEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.llm = LLMEngine()

    def test_regex_email(self):
        """Bug #98: Regex Synthesizer - Email Validation."""
        res = self.llm._deterministic_intent("write a regex for email addresses")
        self.assertIsNotNone(res)
        self.assertIn("Regex", res["spoken_response"])
        self.assertIn("@", res["spoken_response"])

    def test_regex_phone(self):
        """Bug #98: Regex Synthesizer - Phone Number."""
        res = self.llm._deterministic_intent("give me a regex for phone numbers")
        self.assertIsNotNone(res)
        self.assertIn("Regex", res["spoken_response"])
        self.assertIn("Phone", res["spoken_response"])

    def test_sql_top_customers(self):
        """Bug #99: SQL Query Synthesizer - Top Customers."""
        res = self.llm._deterministic_intent("write a sql query for top 5 customers by sales")
        self.assertIsNotNone(res)
        self.assertIn("SELECT", res["spoken_response"])
        self.assertIn("LIMIT 5", res["spoken_response"])
        self.assertIn("INDEX", res["spoken_response"])

    def test_sql_join_users_orders(self):
        """Bug #99: SQL Query Synthesizer - INNER JOIN."""
        res = self.llm._deterministic_intent("sql query to join users and orders")
        self.assertIsNotNone(res)
        self.assertIn("INNER JOIN", res["spoken_response"])

    def test_git_undo_commit(self):
        """Bug #102: Git Command Advisor - Undo Commit."""
        res = self.llm._deterministic_intent("how to undo git commit without losing changes")
        self.assertIsNotNone(res)
        self.assertIn("git reset --soft HEAD~1", res["spoken_response"])

    def test_git_squash(self):
        """Bug #102: Git Command Advisor - Squash Commits."""
        res = self.llm._deterministic_intent("how to git squash commits")
        self.assertIsNotNone(res)
        self.assertIn("rebase -i", res["spoken_response"])

    def test_latex_quadratic(self):
        """Bug #103: LaTeX Formula Synthesizer - Quadratic Formula."""
        res = self.llm._deterministic_intent("quadratic formula in latex")
        self.assertIsNotNone(res)
        self.assertIn("frac{-b", res["spoken_response"])

    def test_latex_schrodinger(self):
        """Bug #103: LaTeX Formula Synthesizer - Schrödinger Equation."""
        res = self.llm._deterministic_intent("schrodinger equation in latex")
        self.assertIsNotNone(res)
        self.assertIn("Psi", res["spoken_response"])

    def test_bash_kill_port(self):
        """Bug #104: Linux Terminal Command - Kill Port."""
        res = self.llm._deterministic_intent("bash command to kill process on port 8080")
        self.assertIsNotNone(res)
        self.assertTrue("fuser" in res["spoken_response"] or "kill" in res["spoken_response"])

    def test_chemistry_h2_o2(self):
        """Bug #105: Chemical Equation Balancer - Water Formation."""
        res = self.llm._deterministic_intent("balance chemical equation H2 + O2 -> H2O")
        self.assertIsNotNone(res)
        self.assertIn("text{H}_2", res["spoken_response"])
        self.assertIn("Formation of Water", res["spoken_response"])

    def test_decision_matrix_postgres_vs_mongodb(self):
        """Bug #107: Decision Matrix - Postgres vs MongoDB."""
        res = self.llm._deterministic_intent("decision matrix postgres vs mongodb")
        self.assertIsNotNone(res)
        self.assertIn("Decision Matrix", res["spoken_response"])
        self.assertIn("PostgreSQL", res["spoken_response"])
        self.assertIn("MongoDB", res["spoken_response"])


if __name__ == "__main__":
    unittest.main()
