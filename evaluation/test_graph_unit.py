import unittest
from unittest.mock import patch

from employee_navigator.graph import (
    ask_for_clarification,
    format_history,
    route_after_analysis,
)


class TestPolicyPilotGraph(unittest.TestCase):

    def test_empty_history(self):
        self.assertEqual(
            format_history([]),
            "No previous conversation."
        )

    def test_history_is_formatted(self):
        history = [
            {"role": "user", "content": "I am joining remotely."},
            {"role": "assistant", "content": "Prepare your setup."},
        ]

        result = format_history(history)

        self.assertIn("user: I am joining remotely.", result)
        self.assertIn("assistant: Prepare your setup.", result)

    def test_history_is_limited_to_recent_ten_messages(self):
        history = [
            {"role": "user", "content": f"message-{i}"}
            for i in range(12)
        ]

        result = format_history(history)

        self.assertNotIn("message-0", result)
        self.assertNotIn("message-1\n", result)
        self.assertIn("message-2", result)
        self.assertIn("message-11", result)

    def test_routes_to_clarification_when_context_is_missing(self):
        state = {"needs_clarification": True}

        self.assertEqual(route_after_analysis(state), "clarify")

    def test_routes_to_retrieval_when_clarification_is_not_needed(self):
        state = {"needs_clarification": False}

        self.assertEqual(route_after_analysis(state), "retrieve")

    def test_clarification_response_contains_missing_context(self):
        state = {
            "clarification_question": "Are you joining remotely or onsite?",
            "missing_context": ["work arrangement"],
        }

        result = ask_for_clarification(state)

        self.assertIn("Are you joining remotely or onsite?", result["answer"])
        self.assertIn("work arrangement", result["answer"])
        self.assertEqual(result["sources"], [])
        self.assertEqual(
            result["evidence_status"],
            "clarification_required",
        )
        self.assertFalse(result["needs_human"])

    def test_clarification_uses_fallback_when_question_is_empty(self):
        result = ask_for_clarification({
            "clarification_question": "   ",
            "missing_context": [],
        })

        self.assertIn(
            "Could you share a little more information",
            result["answer"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
