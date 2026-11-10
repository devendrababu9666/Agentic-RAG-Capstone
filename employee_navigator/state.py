from typing import Any, TypedDict


class ChatMessage(TypedDict, total=False):
    """A message stored in the employee conversation history."""
    role: str
    content: str


class NavigatorState(TypedDict, total=False):
    """Shared state passed between PolicyPilot LangGraph nodes."""

    # Current employee request and conversation context
    question: str
    chat_history: list[ChatMessage]

    # Request understanding and clarification
    topics: list[str]
    missing_context: list[str]
    clarification_question: str
    needs_clarification: bool

    # Retrieved policy evidence
    retrieved_documents: list[dict[str, Any]]
    sources: list[dict[str, str]]

    # Evidence assessment and escalation
    evidence_sufficient: bool
    evidence_status: str
    policy_conflict: bool
    needs_human: bool
    human_reason: str

    # Final employee-facing response
    answer: str
