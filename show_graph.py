
"""
Display and save the Mermaid diagram for the LangGraph workflow.

This script builds the graph and exports its actual node/edge structure.
It does not execute an employee question or generate an LLM response.
"""

from pathlib import Path

from employee_navigator.graph import build_graph


def main() -> None:
    # Compile the workflow defined in graph.py.
    app = build_graph()

    # Ask LangGraph to generate Mermaid syntax from the compiled graph.
    mermaid = app.get_graph().draw_mermaid()

    # Save the diagram source in the project root.
    output_file = Path(__file__).resolve().parent / "workflow.mmd"
    output_file.write_text(mermaid, encoding="utf-8")

    # Print the diagram source so it can also be copied into documentation.
    print("LangGraph Mermaid diagram:")
    print(mermaid)
    print(f"\nDiagram source saved to: {output_file}")


if __name__ == "__main__":
    main()
