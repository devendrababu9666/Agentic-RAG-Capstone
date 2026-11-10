
"""
LangGraph workflow for the Employee Policy and Onboarding Navigator.

Workflow:
    Analyze request
        -> Clarify if essential context is missing
        -> Retrieve relevant policy evidence
        -> Assess evidence sufficiency and conflicts
        -> Generate a grounded answer

The graph controls the workflow. ChromaDB, accessed through rag.py,
provides the policy evidence.
"""

from typing import Literal

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from employee_navigator.config import CHAT_MODEL, validate_config
from employee_navigator.state import NavigatorState
from employee_navigator.rag import retrieve_policy_evidence


# These labels must match the policy categories supported by the app.
ALLOWED_TOPICS = {
    "onboarding",
    "equipment",
    "finance",
    "support",
    "travel",
    "workplace",
}


class RequestAnalysis(BaseModel):
    """Structured output describing the employee's request."""

    topics: list[str] = Field(
        description="Applicable topics from the supported topic list."
    )
    needs_clarification: bool = Field(
        description=(
            "True only when essential missing information prevents "
            "useful and accurate guidance."
        )
    )
    missing_context: list[str] = Field(
        description="Essential details that are missing."
    )
    clarification_question: str = Field(
        description="One concise question to obtain missing information."
    )


class EvidenceAssessment(BaseModel):
    """Structured assessment of retrieved policy passages."""

    evidence_sufficient: bool = Field(
        description=(
            "Whether the evidence adequately supports the important "
            "claims needed to answer the employee's question."
        )
    )
    policy_conflict: bool = Field(
        description=(
            "Whether applicable policy passages materially contradict "
            "each other about the same situation."
        )
    )
    needs_human: bool = Field(
        description=(
            "Whether a policy conflict or important unresolved gap "
            "requires authoritative human clarification."
        )
    )
    human_reason: str = Field(
        description="Reason for recommending human assistance."
    )


def get_model() -> ChatOpenAI:
    """Create the configured OpenAI chat model."""

    validate_config()

    return ChatOpenAI(
        model=CHAT_MODEL,
        temperature=0,
    )


def format_history(history: list[dict[str, str]]) -> str:
    """Format previous messages so the model can interpret follow-ups."""

    if not history:
        return "No previous conversation."

    lines = []

    # Use recent messages to limit unnecessary context.
    for message in history[-10:]:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def analyze_request(state: NavigatorState) -> dict:
    """
    Identify topics and determine whether clarification is required.

    This node does not answer the employee's question.
    It decides how the graph should proceed.
    """

    model = get_model().with_structured_output(RequestAnalysis)

    question = state.get("question", "").strip()
    history = format_history(state.get("chat_history", []))

    prompt = f"""
You are the request-analysis component of an employee policy assistant.

Supported topics:
onboarding, equipment, finance, support, travel, workplace.

Conversation history:
{history}

Latest employee message:
{question}

Instructions:
1. Identify every applicable supported topic.
2. Use conversation history to interpret follow-up messages.
3. Ask for clarification only when missing information materially
   changes the guidance or prevents an accurate answer.
4. Do not ask unnecessary questions if useful general guidance is possible.
5. If clarification is required, ask one concise, specific question.
6. Never invent employee details or company policy rules.
7. Return only topic labels from the supported list.
"""

    result = model.invoke(prompt)

    # Normalize and validate topic names before storing them in state.
    topics = [
        topic.lower().strip()
        for topic in result.topics
        if topic.lower().strip() in ALLOWED_TOPICS
    ]

    return {
        "topics": sorted(set(topics)),
        "needs_clarification": result.needs_clarification,
        "missing_context": result.missing_context,
        "clarification_question": result.clarification_question,
    }


def route_after_analysis(
    state: NavigatorState,
) -> Literal["clarify", "retrieve"]:
    """Route the graph according to the analysis result."""

    if state.get("needs_clarification", False):
        return "clarify"

    return "retrieve"


def ask_for_clarification(state: NavigatorState) -> dict:
    """Return a question when essential employee context is missing."""

    clarification = state.get(
        "clarification_question", ""
    ).strip()

    if not clarification:
        clarification = (
            "Could you share a little more information "
            "about your situation?"
        )

    answer = (
        "To guide you accurately, I need one clarification: "
        f"{clarification}"
    )

    missing = state.get("missing_context", [])

    if missing:
        answer += "\n\nInformation needed: " + ", ".join(missing)

    # This turn ends with a question. The next employee message will
    # be processed in a new graph invocation by the Streamlit app.
    return {
        "answer": answer,
        "sources": [],
        "evidence_status": "clarification_required",
        "evidence_sufficient": False,
        "policy_conflict": False,
        "needs_human": False,
        "human_reason": "",
    }


def retrieve_evidence(state: NavigatorState) -> dict:
    """
    Retrieve relevant passages from the persistent ChromaDB index.

    The query includes recent context so that follow-ups such as
    'What about the laptop?' have a better chance of retrieving
    the correct policy passages.
    """

    question = state.get("question", "").strip()
    history = format_history(state.get("chat_history", []))
    topics = ", ".join(state.get("topics", []))

    retrieval_query = (
        f"Conversation context:\n{history}\n\n"
        f"Employee question:\n{question}\n\n"
        f"Relevant policy topics: {topics}"
    )

    evidence = retrieve_policy_evidence(retrieval_query)

    return {"retrieved_documents": evidence}


def assess_evidence(state: NavigatorState) -> dict:
    """
    Assess evidence sufficiency and possible policy conflicts.

    This is an LLM-based assessment, not a formal guarantee of correctness.
    The separate evaluation tests will help measure its reliability.
    """

    # Initialize the assessor only when retrieved evidence exists.

    question = state.get("question", "")
    evidence = state.get("retrieved_documents", [])

    # Give the assessor source names as well as the retrieved text.
    evidence_text = "\n\n".join(
        (
            f"Source: {item['source_path']}\n"
            f"Category: {item['category']}\n"
            f"Policy text:\n{item['content']}"
        )
        for item in evidence
    )

    if not evidence:
        evidence_text = "No relevant policy passages were retrieved."

    prompt = f"""
You assess evidence for an employee policy assistant.

Employee question:
{question}

Retrieved passages:
{evidence_text}

Assess conservatively.

Rules:
1. Evidence is sufficient only when the passages support the material
   claims required to answer the question.
2. A missing policy statement is not proof of a particular rule.
3. A conflict means applicable passages give materially contradictory
   instructions for the same situation.
4. Different topics or different stages of a process are not automatically
   conflicting.
5. If the requested guidance is absent, mark evidence insufficient.
6. Recommend human assistance for material conflicts or important
   unresolved gaps that require an authoritative decision.
7. Do not invent policy precedence or approval authority.
8. If no relevant evidence was retrieved, do not claim that the policy
   collection definitively lacks the answer; it may be a retrieval failure.
"""

    if evidence:
        model = get_model().with_structured_output(EvidenceAssessment)
        result = model.invoke(prompt)
    else:
        result = None

    # An empty retrieval result is not proof that a policy does not exist.
    # It is, however, insufficient evidence for a policy-backed answer.
    if not evidence:
        evidence_sufficient = False
        policy_conflict = False
        needs_human = True
        human_reason = (
            "No relevant policy passages were retrieved. "
            "The answer cannot be verified from the retrieved evidence. "
            "Try a more specific question or contact the appropriate "
            "support team."
        )
    else:
        evidence_sufficient = result.evidence_sufficient
        policy_conflict = result.policy_conflict
        needs_human = (
            result.needs_human
            or policy_conflict
            or not evidence_sufficient
        )
        human_reason = result.human_reason

    if policy_conflict:
        evidence_status = "conflict"
    elif not evidence_sufficient:
        evidence_status = "insufficient"
    else:
        evidence_status = "supported"

    return {
        "evidence_sufficient": evidence_sufficient,
        "evidence_status": evidence_status,
        "policy_conflict": policy_conflict,
        "needs_human": needs_human,
        "human_reason": human_reason,
    }



def generate_answer(state: NavigatorState) -> dict:
    """Generate a source-grounded response after evidence assessment."""

    model = get_model()

    question = state.get("question", "")
    history = format_history(state.get("chat_history", []))
    evidence = state.get("retrieved_documents", [])

    # Build a distinct list of sources to display in Streamlit.
    sources = []
    seen_sources = set()

    for item in evidence:
        source_key = (
            item["source_path"],
            item["content"],
        )

        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)

        sources.append(
            {
                "source": item["source"],
                "source_path": item["source_path"],
                "category": item["category"],
                "excerpt": item["content"],
            }
        )

    evidence_text = "\n\n".join(
        (
            f"Source: {item['source_path']}\n"
            f"Category: {item['category']}\n"
            f"Policy text:\n{item['content']}"
        )
        for item in evidence
    )

    if not evidence:
        evidence_text = "No policy evidence was retrieved."

    prompt = f"""
You are the Employee Policy and Onboarding Navigator.

Conversation history:
{history}

Latest employee question:
{question}

Retrieved policy evidence:
{evidence_text}

Evidence assessment:
- Sufficient evidence: {state.get('evidence_sufficient', False)}
- Policy conflict detected: {state.get('policy_conflict', False)}
- Human assistance recommended: {state.get('needs_human', False)}
- Reason: {state.get('human_reason', '')}

Response rules:
1. Use the supplied policy passages for company-specific claims.
2. Organize answers by topic when multiple topics are involved.
3. If evidence is insufficient, clearly state what cannot be confirmed.
4. If no passages were retrieved, do not claim the entire policy
   collection lacks the answer.
5. If the policies appear to conflict, explain the uncertainty and
   recommend human clarification rather than choosing a winner.
6. Never invent allowances, deadlines, contacts, benefits or approvals.
7. Identify the source filename supporting each material policy claim.
8. Use previous conversation context for follow-up questions.
9. Give practical next steps only when supported by the evidence.
10. Provide guidance only. Do not claim to approve requests, change
    employee records, or complete tasks on the employee's behalf.
11. If human assistance is recommended, explain why.
"""

    response = model.invoke(prompt)

    return {
        "answer": response.content,
        "sources": sources,
        "evidence_status": state.get("evidence_status", "insufficient"),
        "evidence_sufficient": state.get("evidence_sufficient", False),
        "policy_conflict": state.get("policy_conflict", False),
        "needs_human": state.get("needs_human", False),
        "human_reason": state.get("human_reason", ""),
    }


def build_graph():
    """Register nodes, connect workflow edges, and compile the graph."""

    workflow = StateGraph(NavigatorState)

    # Each node performs one clearly defined responsibility.
    workflow.add_node("analyze", analyze_request)
    workflow.add_node("clarify", ask_for_clarification)
    workflow.add_node("retrieve", retrieve_evidence)
    workflow.add_node("assess", assess_evidence)
    workflow.add_node("answer", generate_answer)

    # Every new graph invocation starts with request analysis.
    workflow.add_edge(START, "analyze")

    # Route to clarification or retrieval based on the analysis.
    workflow.add_conditional_edges(
        "analyze",
        route_after_analysis,
        {
            "clarify": "clarify",
            "retrieve": "retrieve",
        },
    )

    # A clarification question completes this turn.
    workflow.add_edge("clarify", END)

    # Evidence must be retrieved and assessed before answering.
    workflow.add_edge("retrieve", "assess")
    workflow.add_edge("assess", "answer")
    workflow.add_edge("answer", END)

    return workflow.compile()


