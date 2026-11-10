# PolicyPilot
### Agentic RAG Employee Policy & Onboarding Navigator

PolicyPilot is a local-first employee guidance prototype that uses Retrieval-Augmented Generation (RAG) and LangGraph to answer questions about fictional company policies.

It helps employees navigate onboarding, equipment requests, finance and expenses, employee support, business travel, and workplace guidance. Responses are grounded in retrieved policy passages and include source information so users can review the supporting evidence.

> **Important:** PolicyPilot uses fictional classroom policy data. It is a demonstration project, not an official employee-management system. It cannot approve requests, update employee records, verify live request statuses, or perform employee tasks.

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Configuration](#installation-and-configuration)
- [Build the Policy Index](#build-the-policy-index)
- [Run the Application](#run-the-application)
- [Run Tests](#run-tests)
- [Evaluation](#evaluation)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Security Notes](#security-notes)

## Features

- **Policy question answering:** Retrieves relevant passages from the fictional policy collection.
- **Agentic workflow:** Uses LangGraph to coordinate question analysis, clarification, retrieval, evidence assessment, and answer generation.
- **Clarification handling:** Can request additional context when required to interpret a question.
- **Multi-topic guidance:** Supports questions involving more than one policy category.
- **Conversation context:** Uses recent conversation history to help interpret follow-up questions.
- **Source transparency:** Displays policy sources and retrieved excerpts to support review of generated answers.
- **Evidence assessment:** Evaluates whether retrieved evidence is sufficient and whether policy passages conflict.
- **Human escalation:** Can recommend contacting the relevant support team when evidence is insufficient or conflicting.
- **Local vector storage:** Uses ChromaDB to persist the policy index on the local machine.
- **Interactive interface:** Provides a Streamlit chat interface for employee questions.

## Architecture

PolicyPilot separates the user interface, workflow orchestration, retrieval logic, and shared application state.

### Request lifecycle

1. **Analyze:** Interpret the employee's question, identify relevant topics, and determine whether essential context is missing.
2. **Clarify:** Ask a follow-up question when required context is missing.
3. **Retrieve:** Search the ChromaDB policy index for relevant passages.
4. **Assess evidence:** Evaluate evidence sufficiency and possible policy conflicts.
5. **Generate answer:** Produce policy-grounded guidance, expose sources, and communicate when human assistance is appropriate.

The graph can route directly to retrieval when clarification is unnecessary. The evidence assessment is an LLM-based judgment, not a formal guarantee of correctness.

### Architecture components

- **Presentation layer:** Streamlit application in `app.py`.
- **Workflow layer:** LangGraph nodes and routing in `employee_navigator/graph.py`.
- **Retrieval layer:** Document loading, chunking, indexing, and semantic retrieval in `employee_navigator/rag.py`.
- **Configuration:** Model names, index settings, paths, and validation in `employee_navigator/config.py`.
- **Shared state:** Workflow state definitions in `employee_navigator/state.py`.
- **Storage:** Fictional policy documents and a persistent ChromaDB index under `data/`.
- **Evaluation:** Unit tests and test scenarios under `evaluation/`.

The workflow definition is documented in `workflow.mmd`. Open it with a Mermaid-compatible preview to inspect the graph.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and workflow implementation |
| Streamlit | Interactive web interface |
| LangGraph | Workflow orchestration and conditional routing |
| LangChain | Model integration and document-processing components |
| OpenAI API | Language-model responses and text embeddings |
| ChromaDB | Local persistent vector storage and semantic retrieval |
| python-dotenv | Loading local environment configuration |
| unittest | Automated unit tests |

## Project Structure

```text
PolicyPilot/
├── app.py
├── index_policies.py
├── show_graph.py
├── workflow.mmd
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── employee_navigator/
│   ├── __init__.py
│   ├── config.py
│   ├── state.py
│   ├── rag.py
│   └── graph.py
├── data/
│   ├── policies/
│   │   ├── equipment/
│   │   ├── finance/
│   │   ├── onboarding/
│   │   ├── support/
│   │   ├── travel/
│   │   └── workplace/
│   └── vector_store/
├── evaluation/
│   ├── test_scenarios.json
│   ├── test_graph_unit.py
│   ├── test_evidence_assessment.py
│   └── run_evaluation.py
├── reports/
│   ├── evaluation_report.md
│   └── evaluation_run.json
└── Evidence_Screenshots/
```

The `.venv/` directory contains the local Python environment and is intentionally excluded from the documented source tree. Generated cache files and local secrets should not be committed.

## Prerequisites

- Windows with PowerShell, or another environment capable of running Python.
- Python 3.11, matching the environment used during project testing.
- An OpenAI API key with access to the configured chat and embedding models.
- Internet access for OpenAI API requests.
- Git, if you want to version-control the project.

## Installation and Configuration

Open PowerShell in the project root.

### 1. Create a virtual environment

If you do not already have one:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

Check for dependency conflicts:

```powershell
python -m pip check
```

### 3. Configure environment variables

Create a local `.env` file from the example if one does not already exist:

```powershell
if (-not (Test-Path .\.env)) {
    Copy-Item .\.env.example .\.env
}
```

Open `.env` in your editor and configure your own API key and settings.

The configuration supports these variables:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | API authentication |
| `CHAT_MODEL` | Chat and reasoning model |
| `EMBEDDING_MODEL` | Text embedding model |
| `CHUNK_SIZE` | Maximum policy chunk size |
| `CHUNK_OVERLAP` | Overlap between adjacent chunks |
| `RETRIEVAL_K` | Number of policy passages requested during retrieval |
| `MAX_HISTORY_MESSAGES` | Maximum recent messages retained for context |

The current defaults in the application are `gpt-4.1` for chat, `text-embedding-3-large` for embeddings, a chunk size of `1000`, overlap of `150`, retrieval count of `8`, and history limit of `10`.

Never publish your real API key.

## Build the Policy Index

The fictional policy files are stored under `data/policies/`.

To create or deliberately rebuild the vector index, run:

```powershell
python .\index_policies.py
```

The indexing process loads the policy documents, splits them into chunks, generates embeddings, and stores the index in `data/vector_store/`.

Rebuilding can make embedding API requests and incur costs. Do not run the indexing script for every employee question. The application also checks whether the index needs rebuilding when loading it.

Keep the existing vector store if you want to reuse the current index.

## Run the Application

With the virtual environment activated, run:

```powershell
python -m streamlit run .\app.py
```

Open the local URL printed in the terminal, usually:

```text
http://localhost:8501
```

Ask a question about the fictional policies and inspect the generated answer, evidence status, and supporting sources.

### Example questions

```text
What equipment should I prepare before joining remotely?
```

```text
How do I check the status of an equipment request?
```

```text
How should I report a missing expense receipt?
```

```text
What should I do if my business travel booking changes?
```

```text
How much will the company reimburse me for home internet?
```

The last question is useful for checking whether the assistant acknowledges a gap in the available policies rather than inventing a reimbursement amount.

## Run Tests

Run the unit-test suite from the project root:

```powershell
python -m unittest discover -s evaluation -p "test_*.py" -v
```

Compile the application and evaluation modules:

```powershell
python -m compileall -q .\app.py .\index_policies.py .\show_graph.py .\employee_navigator .\evaluation
```

A successful compilation command produces no syntax-error output.

### Verified development checks

During development, the following checks were observed:

- **11 unit tests passed** across graph utilities, clarification routing, and evidence assessment.
- Python syntax compilation completed successfully.
- A similarity search retrieved relevant passages from the equipment policy.
- The LangGraph workflow completed an equipment-guidance question and returned sources with a supported evidence status.
- The Streamlit interface rendered a policy-grounded answer with source information.

These are development checks, not proof that every evaluation scenario passes or that the system is error-free.

## Evaluation

Evaluation scenarios are defined in `evaluation/test_scenarios.json`. The unit tests are maintained separately in the same directory.

The evaluation scenarios address behaviors such as:

- Basic policy retrieval
- Clarification when context is missing
- Multi-topic questions
- Contextual follow-up questions
- Missing policy information
- Contradictory evidence
- Unsupported actions and human escalation
- Source relevance
- Index persistence and freshness
- Configuration validation

The evaluation runner and reports support further testing and documentation. Each scenario should be marked as passing only after its actual output has been checked against its expected behavior.

Review `reports/evaluation_report.md` for the project's evaluation documentation.

## Limitations

- **Fictional data:** The policy collection is designed for demonstration and does not represent a real employer's official policies.
- **Model judgment:** Evidence sufficiency, conflict detection, and generated answers depend partly on language-model behavior.
- **Retrieval limitations:** Relevant policy passages may be missed, so a lack of retrieved evidence does not prove that a policy does not exist.
- **No live employee systems:** The assistant cannot retrieve live request statuses or update employee records.
- **No autonomous approvals:** It cannot approve equipment, expenses, travel, access permissions, or other employee requests.
- **Human review:** Unresolved policy gaps and material conflicts should be referred to the appropriate support team.
- **API dependency:** Configured OpenAI model calls require API access and may incur usage charges.
- **Local persistence:** The vector index is stored locally; multi-user deployment, access control, and production-grade operational monitoring require additional engineering.

## Future Improvements

Potential next steps include:

- Expand automated tests for missing evidence, contradictory passages, and unsupported actions.
- Evaluate retrieval precision, source relevance, and answer faithfulness with a repeatable benchmark.
- Add automated checks for policy freshness and source metadata integrity.
- Improve user-facing citations and evidence explanations.
- Add structured logging and clearer error reporting.
- Introduce authentication and authorization before any real organizational deployment.
- Add privacy controls, retention policies, and production deployment safeguards.
- Evaluate model behavior against adversarial and ambiguous employee questions.

These are proposed improvements, not claims that the functionality is already implemented.

## Security Notes

- Keep `.env` out of version control.
- Use `.env.example` only as a template with placeholder values.
- Do not expose API keys in screenshots, logs, source files, or reports.
- Review `.gitignore` before committing the project.
- Do not use the fictional policies as authoritative guidance for real employee decisions.

---

**PolicyPilot** — an agentic RAG prototype for employee policy navigation and onboarding guidance.
