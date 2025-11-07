#!/usr/bin/env python
"""Simple Retrieval QA that uses MemMachine memories as knowledge base."""

from __future__ import annotations

import argparse

from demo_conversation import get_chat_model
from memmachine_retriever import MemMachineRetriever

PROMPT_TEMPLATE = """You are an analyst answering questions about supplier {supplier_id}.
If the context does not contain the answer, say you do not know.

Context:
{context}

Question: {question}
Answer:"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Question to ask about the supplier")
    parser.add_argument(
        "--supplier-id",
        default="SUP-202",
        help="Supplier identifier (used for prompt context).",
    )
    parser.add_argument(
        "--session-id",
        help="Optional MemMachine session id to scope the search (e.g. profile_ops).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of memories to retrieve from MemMachine.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    retriever = MemMachineRetriever(session_id=args.session_id, limit=args.limit)
    docs = retriever.invoke(args.question)

    context = "\n\n".join(doc.page_content for doc in docs) or "(No relevant context found)"

    prompt = PROMPT_TEMPLATE.format(
        supplier_id=args.supplier_id,
        context=context,
        question=args.question,
    )

    response = get_chat_model().invoke(prompt)

    print("=== Answer ===")
    print(response.content.strip())

    print("\n=== Sources ===")
    if docs:
        for doc in docs:
            print("-", doc.page_content.replace("\n", " "))
    else:
        print("(No documents returned)")


if __name__ == "__main__":
    main()
