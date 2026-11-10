"""
Build or rebuild the local employee policy vector database.

Run this script after adding, editing, or removing policy documents.
The RAG module manages the target Chroma collection and index manifest.
"""

from employee_navigator.rag import create_vector_store


def main() -> None:
    print("Building the policy vector database...")
    create_vector_store()
    print("Policy indexing completed successfully.")


if __name__ == "__main__":
    main()
