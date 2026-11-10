import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from employee_navigator.graph import assess_evidence


class TestEvidenceAssessment(unittest.TestCase):

    @patch("employee_navigator.graph.get_model")
    def test_no_evidence_marks_answer_insufficient(self, mock_get_model):
        result = assess_evidence({
            "question": "What is the reimbursement amount?",
            "retrieved_documents": [],
        })

        self.assertFalse(result["evidence_sufficient"])
        self.assertFalse(result["policy_conflict"])
        self.assertEqual(result["evidence_status"], "insufficient")
        self.assertTrue(result["needs_human"])
        self.assertIn("No relevant policy passages", result["human_reason"])
        mock_get_model.assert_not_called()

    @patch("employee_navigator.graph.get_model")
    def test_insufficient_evidence_recommends_human_help(
        self, mock_get_model
    ):
        model = MagicMock()
        model.with_structured_output.return_value.invoke.return_value = (
            SimpleNamespace(
                evidence_sufficient=False,
                policy_conflict=False,
                needs_human=False,
                human_reason="The policy does not specify the amount.",
            )
        )
        mock_get_model.return_value = model

        evidence = [{
            "source_path": "finance/reimbursement_policy.txt",
            "category": "finance",
            "content": "Employees must submit eligible expenses for review.",
        }]

        result = assess_evidence({
            "question": "What is the exact reimbursement amount?",
            "retrieved_documents": evidence,
        })

        self.assertFalse(result["evidence_sufficient"])
        self.assertEqual(result["evidence_status"], "insufficient")
        self.assertTrue(result["needs_human"])
        self.assertEqual(
            result["human_reason"],
            "The policy does not specify the amount.",
        )

    @patch("employee_navigator.graph.get_model")
    def test_conflicting_evidence_sets_conflict_status(
        self, mock_get_model
    ):
        model = MagicMock()
        model.with_structured_output.return_value.invoke.return_value = (
            SimpleNamespace(
                evidence_sufficient=True,
                policy_conflict=True,
                needs_human=False,
                human_reason="The policy passages specify different deadlines.",
            )
        )
        mock_get_model.return_value = model

        evidence = [
            {
                "source_path": "finance/policy_a.txt",
                "category": "finance",
                "content": "Submit claims within 10 days.",
            },
            {
                "source_path": "finance/policy_b.txt",
                "category": "finance",
                "content": "Submit claims within 20 days.",
            },
        ]

        result = assess_evidence({
            "question": "What is the expense claim deadline?",
            "retrieved_documents": evidence,
        })

        self.assertTrue(result["policy_conflict"])
        self.assertEqual(result["evidence_status"], "conflict")
        self.assertTrue(result["needs_human"])

    @patch("employee_navigator.graph.get_model")
    def test_supported_evidence_preserves_supported_status(
        self, mock_get_model
    ):
        model = MagicMock()
        model.with_structured_output.return_value.invoke.return_value = (
            SimpleNamespace(
                evidence_sufficient=True,
                policy_conflict=False,
                needs_human=False,
                human_reason="",
            )
        )
        mock_get_model.return_value = model

        evidence = [{
            "source_path": "equipment/laptop_policy.txt",
            "category": "equipment",
            "content": "Report an undelivered laptop to IT support.",
        }]

        result = assess_evidence({
            "question": "What should I do if my laptop is undelivered?",
            "retrieved_documents": evidence,
        })

        self.assertTrue(result["evidence_sufficient"])
        self.assertEqual(result["evidence_status"], "supported")
        self.assertFalse(result["policy_conflict"])
        self.assertFalse(result["needs_human"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
