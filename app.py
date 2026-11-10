import streamlit as st
from html import escape

from employee_navigator.config import validate_config
from employee_navigator.graph import build_graph

st.set_page_config(
    page_title="PolicyPilot | PolicyPilot | Employee Policy Assistant",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual identity ----------
st.markdown("""
<style>
    :root {
        --pp-primary: #2563eb;
        --pp-primary-dark: #1d4ed8;
        --pp-ink: #172033;
        --pp-muted: #64748b;
        --pp-border: #dbe4f0;
        --pp-surface: #ffffff;
        --pp-page: #f3f6fb;
    }

    .stApp {
        background: var(--pp-page);
        color: var(--pp-ink);
    }

    [data-testid="stHeader"] {
        background: rgba(243,246,251,0.94);
    }

    .block-container {
        max-width: 1260px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111c30;
        border-right: 1px solid #25344b;
    }

    [data-testid="stSidebar"] * {
        color: #e6edf8;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #aab9cf;
    }

    [data-testid="stSidebar"] hr {
        border-color: #2b3a50;
    }

    /* Brand */
    .brand {
        display: block;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        line-height: 1.45;
        padding-top: 5px;
        padding-bottom: 4px;
        margin: 0;
        color: #1d4ed8;
        overflow: visible;
        overflow-wrap: anywhere;
    }

    .brand-sub {
        display: block;
        color: #64748b;
        font-size: .72rem;
        letter-spacing: 1.2px;
        font-weight: 650;
        line-height: 1.6;
        margin-top: 2px;
    }

    .brand-sub {
        color: #71839d;
        font-size: .72rem;
        letter-spacing: 1.5px;
        font-weight: 650;
    }

    /* Hero banner */
    .hero {
        background: linear-gradient(120deg, #14243d 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 2rem 2.2rem;
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 20px;
        margin: .8rem 0 1.7rem 0;
        box-shadow: 0 12px 32px rgba(30,64,175,.10);
    }

    .hero h1 {
        color: #ffffff;
        font-size: clamp(1.8rem, 3vw, 2.5rem);
        line-height: 1.16;
        letter-spacing: -1px;
        margin: .65rem 0;
    }

    .hero p {
        color: #e0eaff;
        font-size: .98rem;
        line-height: 1.75;
        max-width: 760px;
    }

    .eyebrow {
        color: #bfdbfe;
        font-size: .73rem;
        letter-spacing: 2px;
        font-weight: 750;
    }

    .section-title {
        color: #172033;
        font-size: 1.3rem;
        font-weight: 750;
        margin: 1.2rem 0 .3rem 0;
    }

    .section-sub {
        color: #64748b;
        font-size: .9rem;
        margin-bottom: 1rem;
    }

    /* Service cards */
    .service-card {
        background: #ffffff;
        border: 1px solid #dce5f0;
        border-radius: 16px;
        padding: 1.2rem;
        min-height: 132px;
        transition: border-color .18s ease, box-shadow .18s ease;
    }

    .service-card:hover {
        border-color: #93b4f8;
        box-shadow: 0 8px 24px rgba(30,64,175,.08);
    }

    .service-icon {
        font-size: 1.5rem;
        margin-bottom: .65rem;
    }

    .service-title {
        color: #172033;
        font-weight: 750;
        margin-bottom: .4rem;
    }

    .service-desc {
        color: #64748b;
        font-size: .85rem;
        line-height: 1.5;
    }

    /* Consistent buttons, including Streamlit's default red primary */
    div.stButton > button,
    [data-testid="stSidebar"] div.stButton > button {
        border-radius: 10px;
        min-height: 2.65rem;
        font-weight: 600;
        border: 1px solid #d7e1ef;
        transition: all .16s ease;
    }

    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="stBaseButton-primary"],
    [data-testid="stSidebar"] div.stButton > button[kind="primary"],
    [data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"] {
        background: #2563eb;
        color: #ffffff;
        border-color: #2563eb;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: #1d4ed8;
        border-color: #1d4ed8;
        color: #ffffff;
    }

    div.stButton > button[kind="secondary"],
    div.stButton > button[data-testid="stBaseButton-secondary"] {
        background: #ffffff;
        color: #334155;
    }

    div.stButton > button[kind="secondary"]:hover,
    div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: #eff6ff;
        border-color: #93b4f8;
        color: #1d4ed8;
    }

    /* Chat and evidence */
    [data-testid="stChatMessage"] {
        background: #ffffff;
        border: 1px solid #e0e7f1;
        border-radius: 15px;
        padding: .9rem 1rem;
        margin-bottom: .8rem;
    }

    [data-testid="stChatInput"] {
        border-color: #cbd8ea;
        border-radius: 14px;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #2563eb;
        box-shadow: 0 0 0 1px #2563eb;
    }

    [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #dce5f0;
        border-radius: 12px;
    }

    .notice {
        background: #eaf2ff;
        border: 1px solid #c6dbff;
        color: #1e40af;
        padding: .95rem 1rem;
        border-radius: 12px;
        font-size: .88rem;
        line-height: 1.6;
        margin: 1.2rem 0;
    }

    .footer-note {
        color: #8290a5;
        font-size: .78rem;
        text-align: center;
        margin-top: 2rem;
    }

    /* Small screens */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
        }

        .hero {
            padding: 1.4rem;
            border-radius: 15px;
        }

        .hero h1 {
            font-size: 1.8rem;
        }

        .service-card {
            min-height: 115px;
            padding: .9rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ---------- Graph lifecycle ----------
@st.cache_resource
def get_graph():
    return build_graph()


# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="brand" style="color:#93c5fd">PolicyPilot</div>'
        '<div class="brand-sub" style="color:#cbd5e1">'
        'EMPLOYEE POLICY & ONBOARDING</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("### Your workspace")
    st.caption("Find guidance for your employee journey.")

    pages = {
        "Overview": "Overview",
        "Policy assistant": "Policy assistant",
        "Supported services": "Supported services",
    }

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Overview"

    for label, value in pages.items():
        if st.button(
            label,
            key=f"nav_{value}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.active_page == value
                else "secondary"
            ),
        ):
            st.session_state.active_page = value
            st.rerun()

    st.divider()
    st.markdown("### Conversation")
    st.caption(f"{len(st.session_state.messages)} messages in this session")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.divider()
    st.caption("Demo environment")
    st.caption("Fictional company policies")
    st.caption("No employee records are changed")


# ---------- Reusable policy source display ----------
def render_evidence_status(status, needs_human=False, human_reason=""):
    """Show the workflow's evidence assessment to the employee."""
    labels = {
        "supported": ("Supported by retrieved evidence", "success"),
        "insufficient": ("Evidence is insufficient", "warning"),
        "conflict": ("Conflicting policy guidance detected", "error"),
        "clarification_required": ("More information is needed", "info"),
    }

    label, level = labels.get(
        status,
        ("Evidence status unavailable", "info"),
    )

    getattr(st, level)(label)

    if needs_human:
        reason = human_reason or (
            "Please contact the appropriate support team to confirm the guidance."
        )
        st.warning("Human assistance recommended: " + reason)


def render_sources(sources):
    if not sources:
        st.info(
            "No supporting policy excerpts were returned. "
            "Treat the answer as unverified."
        )
        return

    with st.expander(
        f"Evidence and policy sources ({len(sources)})",
        expanded=False,
    ):
        for i, source in enumerate(sources, start=1):
            if not isinstance(source, dict):
                continue

            filename = str(
                source.get("source_path", "Unknown source")
            )
            category = str(
                source.get("category", "Unclassified")
            )
            excerpt = str(
                source.get("excerpt", "No excerpt available.")
            )

            st.markdown(f"**{i}. {filename}**")
            st.caption(f"Policy category: {category}")
            st.write(excerpt)

            if i < len(sources):
                st.divider()


# ---------- Header ----------
left, right = st.columns([3, 1])

with left:
    st.markdown(
        '<div class="brand">PolicyPilot</div>'
        '<div class="brand-sub">EMPLOYEE POLICY & ONBOARDING</div>',
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        "<div style='text-align:right;padding-top:12px;color:#64748b'>"
        "● Policy assistant</div>",
        unsafe_allow_html=True,
    )


# ---------- Page: Overview ----------
if st.session_state.active_page == "Overview":
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">YOUR EMPLOYEE SUPPORT HUB</div>
        <h1>Your workplace,<br>made simpler.</h1>
        <p>
            Get onboarding guidance, understand workplace policies,
            and discover your next steps with answers grounded in
            your fictional company policy documents.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">What can we help you with?</div>'
        '<div class="section-sub">Choose a service or ask a question.</div>',
        unsafe_allow_html=True,
    )

    services = [
        ("💻", "Equipment & IT", "Devices, access and remote setup",
         "What equipment should I prepare before joining remotely?"),
        ("🧭", "Onboarding", "First-day preparation and formalities",
         "What should I complete before my first day at work?"),
        ("✈️", "Travel & expenses", "Business trips and expense guidance",
         "What should I check before arranging business travel?"),
        ("🏢", "Workplace", "Working arrangements and office guidance",
         "What workplace arrangements should a new employee know?"),
        ("💳", "Finance", "Allowances and reimbursement policies",
         "What does the policy say about employee reimbursements?"),
        ("🤝", "Employee support", "Find the right support team",
         "Who should I contact if my onboarding issue is unresolved?"),
    ]

    for row_start in range(0, len(services), 3):
        columns = st.columns(3, gap="medium")

        for col, item in zip(
            columns, services[row_start:row_start + 3]
        ):
            icon, title, desc, question = item

            with col:
                st.markdown(
                    f'<div class="service-card">'
                    f'<div class="service-icon">{icon}</div>'
                    f'<div class="service-title">{escape(title)}</div>'
                    f'<div class="service-desc">{escape(desc)}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Explore service →",
                    key=f"service_{row_start}_{title}",
                    use_container_width=True,
                ):
                    st.session_state.active_page = "Policy assistant"
                    st.session_state.pending_question = question
                    st.rerun()

    st.markdown(
        '<div class="notice">'
        '<b>Evidence first.</b> PolicyPilot provides guidance, not approvals. '
        'If a policy is missing or conflicting, the assistant should '
        'identify the limitation and direct you to human support.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Start with a question</div>'
        '<div class="section-sub">Common employee scenarios</div>',
        unsafe_allow_html=True,
    )

    quick_questions = [
        "I'm joining remotely. What should I prepare?",
        "What should I arrange before a business trip?",
        "The policy doesn't mention my allowance. What should I do?",
    ]

    for i, question in enumerate(quick_questions):
        if st.button(
            question,
            key=f"quick_{i}",
            use_container_width=True,
        ):
            st.session_state.active_page = "Policy assistant"
            st.session_state.pending_question = question
            st.rerun()


# ---------- Page: Supported services ----------
elif st.session_state.active_page == "Supported services":
    st.markdown(
        '<div class="hero">'
        '<div class="eyebrow">POLICY DIRECTORY</div>'
        '<h1>Explore employee services.</h1>'
        '<p>Browse the supported topics and ask questions about '
        'the available policy documents.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    categories = [
        ("Onboarding", "Joining formalities and first-day preparation."),
        ("Equipment", "Devices, equipment arrangements and IT access."),
        ("Finance", "Allowances, reimbursements and expense guidance."),
        ("Support", "Escalation routes and employee assistance."),
        ("Travel", "Business travel arrangements and requirements."),
        ("Workplace", "Workplace arrangements and working guidance."),
    ]

    for name, description in categories:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.write(description)

            if st.button(
                f"Ask about {name.lower()}",
                key=f"ask_category_{name}",
            ):
                st.session_state.active_page = "Policy assistant"
                st.session_state.pending_question = (
                    f"What do the available {name.lower()} policies say?"
                )
                st.rerun()


# ---------- Page: Policy assistant ----------
else:
    st.markdown(
        '<div class="section-title">Policy assistant</div>'
        '<div class="section-sub">Ask a question, add context, '
        'and review the evidence behind the answer.</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "The assistant uses fictional policies. It cannot approve "
        "requests, update employee records, or complete tasks."
    )

    if not st.session_state.messages:
        st.markdown("#### How can I help today?")
        st.caption(
            "You can ask about several topics in one question. "
            "If essential context is missing, the assistant may ask "
            "a follow-up question."
        )

    # Render conversation history.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_evidence_status(
                    message.get("evidence_status", "insufficient"),
                    message.get("needs_human", False),
                    message.get("human_reason", ""),
                )
                render_sources(message.get("sources", []))

    typed_question = st.chat_input(
        "Ask about onboarding, equipment, finance, travel..."
    )

    question = (
        st.session_state.pending_question or typed_question
    )

    if question:
        st.session_state.pending_question = None

        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                validate_config()
                graph = get_graph()

                previous_messages = st.session_state.messages[:-1]

                chat_history = [
                    {
                        "role": message["role"],
                        "content": message["content"],
                    }
                    for message in previous_messages[-10:]
                ]

                with st.spinner(
                    "Analyzing your request and reviewing policy evidence..."
                ):
                    result = graph.invoke({
                        "question": question,
                        "chat_history": chat_history,
                    })

                answer = result.get("answer") or (
                    "I could not generate a response. "
                    "Please try again."
                )
                sources = result.get("sources") or []

                evidence_status = result.get(
                    "evidence_status", "insufficient"
                )
                needs_human = result.get("needs_human", False)
                human_reason = result.get("human_reason", "")

                st.markdown(answer)
                render_evidence_status(
                    evidence_status,
                    needs_human,
                    human_reason,
                )
                render_sources(sources)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "evidence_status": evidence_status,
                    "needs_human": needs_human,
                    "human_reason": human_reason,
                })

            except Exception as exc:
                st.error(
                    "The request could not be completed. Check your "
                    "API configuration, policy index, and terminal output."
                )
                print(
                    f"Application error: {type(exc).__name__}: {exc}"
                )

    st.markdown(
        '<div class="footer-note">'
        'PolicyPilot · Employee guidance prototype · Fictional policy data'
        '</div>',
        unsafe_allow_html=True,
    )



