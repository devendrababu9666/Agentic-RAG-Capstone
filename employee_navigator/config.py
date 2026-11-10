
"""
Application configuration.

This module centralizes model settings, policy paths, and RAG parameters.
Keeping configuration in one place makes the project easier to maintain.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Find the project root directory.
# config.py is inside employee_navigator/, so its parent directory is
# the project root containing app.py and the .env file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables from the project's .env file.
# This lets us use the OpenAI API key without hardcoding it in Python.
load_dotenv(PROJECT_ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Model settings can be overridden in the project-root .env file.
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1").strip()
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-large",
).strip()

# Directory containing the supplied fictional policy documents.
POLICY_DIR = PROJECT_ROOT / "data" / "policies"

# Directory where ChromaDB will persist the policy vector index.
# The saved embeddings and metadata will survive application restarts.
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"

# RAG configuration. Validate numeric values before indexing.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "8"))

# Keep conversation context manageable.
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))


def validate_config() -> None:
    """Check required configuration before making API calls."""

    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is missing. "
            "Add your API key to the project-root .env file."
        )

    if not CHAT_MODEL:
        raise ValueError("CHAT_MODEL must not be empty.")

    if not EMBEDDING_MODEL:
        raise ValueError("EMBEDDING_MODEL must not be empty.")

    if CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")

    if CHUNK_OVERLAP < 0 or CHUNK_OVERLAP >= CHUNK_SIZE:
        raise ValueError(
            "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE."
        )

    if RETRIEVAL_K <= 0:
        raise ValueError("RETRIEVAL_K must be greater than zero.")

    if MAX_HISTORY_MESSAGES <= 0:
        raise ValueError("MAX_HISTORY_MESSAGES must be greater than zero.")

    if not POLICY_DIR.is_dir():
        raise FileNotFoundError(
            f"Policy directory not found: {POLICY_DIR}"
        )
