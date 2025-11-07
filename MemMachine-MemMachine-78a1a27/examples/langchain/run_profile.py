#!/usr/bin/env python
"""Command-line helper to run a LangChain persona against MemMachine."""

from __future__ import annotations

import argparse
from typing import Optional

from demo_conversation import (
    PERSONA_PROMPTS,
    conversation_chain,
    resolve_system_prompt,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a LangChain profile conversation backed by MemMachine."
    )
    parser.add_argument(
        "question",
        help="Prompt to send to the persona",
    )
    parser.add_argument(
        "--profile",
        default="supplier-demo",
        help=(
            "Session/profile id (e.g. profile_sales, profile_ops, profile_manager). "
            "Defaults to supplier-demo."
        ),
    )
    parser.add_argument(
        "--history-limit",
        type=int,
        default=5,
        help="Number of recent messages to hydrate from MemMachine before asking the question.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chain = conversation_chain()
    config = {
        "configurable": {
            "session_id": args.profile,
            "history_limit": args.history_limit,
        }
    }
    response = chain.invoke(
        {
            "input": args.question,
            "system_prompt": resolve_system_prompt(args.profile),
        },
        config=config,
    )

    print("=== Persona:", args.profile, "===")
    print(response.content)


if __name__ == "__main__":
    main()
