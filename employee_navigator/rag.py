from pathlib import Path

"""
Persistent RAG pipeline for employee policies.

Initial indexing:
    Read policy files -> split into chunks -> embed -> save to ChromaDB.

Normal application use:
    Load ChromaDB -> embed the new query -> retrieve relevant chunks.

Document embeddings are reused across application restarts.
"""

import hashlib
import json

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from employee_navigator.config import (
    EMBEDDING_MODEL,
    POLICY_DIR,
    VECTOR_STORE_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_K,
    validate_config,
)


# Only ingest formats supported by this prototype.
SUPPORTED_EXTENSIONS = {".txt", ".md"}

# Name of the collection inside the local Chroma database.
COLLECTION_NAME = "employee_policies"


MANIFEST_NAME = ".policy_manifest.json"


def _policy_fingerprint() -> str:
    """Fingerprint policy content and indexing settings."""
    digest = hashlib.sha256()

    for file_path in sorted(POLICY_DIR.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if file_path.name.lower() == "readme.md":
            continue

        relative_path = str(file_path.relative_to(POLICY_DIR))
        digest.update(relative_path.encode("utf-8"))
        digest.update(file_path.read_bytes())

    settings = {
        "embedding_model": EMBEDDING_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "collection": COLLECTION_NAME,
    }
    digest.update(
        json.dumps(settings, sort_keys=True).encode("utf-8")
    )
    return digest.hexdigest()


def _manifest_path() -> Path:
    return VECTOR_STORE_DIR / MANIFEST_NAME


def load_policy_documents() -> list[Document]:
    """Load policy files and preserve source metadata."""

    if not POLICY_DIR.exists():
        raise FileNotFoundError(
            f"Policy directory not found: {POLICY_DIR}"
        )

    documents = []

    # Search recursively to include every policy category.
    for path in sorted(POLICY_DIR.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # Do not index a README as a company policy.
        if path.name.lower() == "readme.md":
            continue

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        ).strip()

        if not text:
            continue

        # Preserve the source filename and category for citations.
        category = (
            path.parent.name
            if path.parent != POLICY_DIR
            else "uncategorized"
        )

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": path.name,
                    "source_path": str(path.relative_to(POLICY_DIR)),
                    "category": category,
                },
            )
        )

    if not documents:
        raise ValueError(
            f"No readable policy files found in {POLICY_DIR}"
        )

    return documents


def split_policy_documents(
    documents: list[Document],
) -> list[Document]:
    """Split long policies into overlapping searchable chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )

    return splitter.split_documents(documents)


def create_vector_store() -> Chroma:
    """Build a fresh local index from the current policy files."""
    validate_config()

    documents = load_policy_documents()
    chunks = split_policy_documents(documents)

    if not chunks:
        raise ValueError("No policy chunks were produced for indexing.")

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    # Remove only the target collection, preserving the Chroma database.
    try:
        existing_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(VECTOR_STORE_DIR),
        )
        existing_store.delete_collection()
    except Exception:
        # The collection may not exist yet. Chroma will create it below.
        pass

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    # Write the manifest only after indexing succeeds.
    manifest = {
        "fingerprint": _policy_fingerprint(),
        "document_count": len(documents),
        "chunk_count": len(chunks),
    }
    _manifest_path().write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print(f"Policy documents loaded: {len(documents)}")
    print(f"Chunks indexed: {len(chunks)}")
    print(f"Vector database location: {VECTOR_STORE_DIR}")

    return vector_store


def load_vector_store() -> Chroma:
    """Open an existing local index without re-embedding documents."""

    validate_config()

    database_file = VECTOR_STORE_DIR / "chroma.sqlite3"

    if not database_file.exists():
        raise FileNotFoundError(
            "No saved vector database found. "
            "Run 'python index_policies.py' first."
        )

    # This embedding model is used for new search queries.
    # Existing document embeddings remain stored in ChromaDB.
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )


def get_vector_store() -> Chroma:
    """Load a current index or rebuild it when policies/settings change."""
    validate_config()

    database_file = VECTOR_STORE_DIR / "chroma.sqlite3"
    manifest_file = _manifest_path()
    current_fingerprint = _policy_fingerprint()

    if database_file.exists() and manifest_file.exists():
        try:
            manifest = json.loads(
                manifest_file.read_text(encoding="utf-8")
            )
            if manifest.get("fingerprint") == current_fingerprint:
                return load_vector_store()
        except (OSError, ValueError, TypeError):
            # A missing or invalid manifest requires a fresh index.
            pass

    print("Policy index is missing or outdated. Rebuilding it...")
    return create_vector_store()


def retrieve_policy_evidence(
    question: str,
    k: int = RETRIEVAL_K,
) -> list[dict[str, str]]:
    """Return relevant policy chunks with source details."""

    if not question.strip():
        return []

    vector_store = get_vector_store()

    # Chroma compares the query embedding against saved policy embeddings.
    matches = vector_store.similarity_search(
        question,
        k=k,
    )

    # Convert retrieved documents into a predictable structure for LangGraph.
    return [
        {
            "content": document.page_content,
            "source": document.metadata.get("source", "Unknown"),
            "source_path": document.metadata.get(
                "source_path", "Unknown"
            ),
            "category": document.metadata.get(
                "category", "Unknown"
            ),
        }
        for document in matches
    ]

