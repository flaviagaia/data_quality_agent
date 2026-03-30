from __future__ import annotations

import unittest

from src.agent import ask_data_quality_agent
from src.sample_data import ensure_sample_data
from src.tools import suggest_record_corrections, validate_record_fields


class DataQualityAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        ensure_sample_data()

    def test_validation_returns_issues_for_bad_record(self) -> None:
        validation = validate_record_fields("DQ-1002")
        self.assertGreaterEqual(validation["issue_count"], 1)
        self.assertIn("email_invalido", validation["issues"])

    def test_corrections_return_status(self) -> None:
        corrections = suggest_record_corrections("DQ-1001")
        self.assertIn("status_recommendation", corrections)

    def test_agent_returns_final_message(self) -> None:
        result = ask_data_quality_agent(
            record_id="DQ-1003",
            user_question="Existe algum problema crítico nesse registro?",
        )
        self.assertIn("runtime_mode", result)
        self.assertIn("final_message", result)
        self.assertIn("record_id", result)


if __name__ == "__main__":
    unittest.main()
