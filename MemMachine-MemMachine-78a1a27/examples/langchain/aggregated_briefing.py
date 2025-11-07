#!/usr/bin/env python
"""Generate a leadership briefing by orchestrating multiple LangChain personas."""

from __future__ import annotations

import argparse
from typing import Dict

from langchain_core.prompts import ChatPromptTemplate

from demo_conversation import conversation_chain, get_chat_model, resolve_system_prompt
from memmachine_memory import MemMachineChatMessageHistory


DEFAULT_PROMPTS: Dict[str, str] = {
    "profile_sales": "Summarize outstanding negotiations for supplier {supplier_id}.",
    "profile_ops": "Flag any logistics risks for supplier {supplier_id}.",
    "profile_manager": "Create a leadership briefing draft for supplier {supplier_id}.",
}

BRIEFING_PROMPT = ChatPromptTemplate.from_template(
    """You are a Chief-of-Staff preparing a concise leadership briefing.
Specialist reports:
- Sales: {sales}
- Operations: {ops}
- Account Manager: {manager}

Write an action-oriented briefing for supplier {supplier_id} with sections:
1. Executive Summary
2. Key Risks
3. Recommended Actions
4. Follow-Up Owners
Keep it under 250 words.
"""
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("supplier_id", help="Supplier identifier, e.g. SUP-202")
    parser.add_argument(
        "--history-limit",
        type=int,
        default=5,
        help="Number of recent persona messages to hydrate before asking.",
    )
    return parser.parse_args()


def run_persona(session_id: str, prompt_template: str, supplier_id: str, history_limit: int) -> str:
    chain = conversation_chain(default_session_id=session_id, history_limit=history_limit)
    prompt = prompt_template.format(supplier_id=supplier_id)
    response = chain.invoke(
        {
            "input": prompt,
            "system_prompt": resolve_system_prompt(session_id),
        },
        config={
            "configurable": {
                "session_id": session_id,
                "history_limit": history_limit,
            }
        },
    )
    return response.content


def store_briefing(text: str, supplier_id: str) -> None:
    history = MemMachineChatMessageHistory(session_id="profile_leadership", load_remote_history=True)
    history.add_user_message(f"Leadership briefing requested for {supplier_id}")
    history.add_ai_message(text)


def main() -> None:
    args = parse_args()
    supplier_id = args.supplier_id
    history_limit = args.history_limit

    sales = run_persona("profile_sales", DEFAULT_PROMPTS["profile_sales"], supplier_id, history_limit)
    ops = run_persona("profile_ops", DEFAULT_PROMPTS["profile_ops"], supplier_id, history_limit)
    manager = run_persona("profile_manager", DEFAULT_PROMPTS["profile_manager"], supplier_id, history_limit)

    prompt_value = BRIEFING_PROMPT.invoke(
        {
            "sales": sales,
            "ops": ops,
            "manager": manager,
            "supplier_id": supplier_id,
        }
    )
    model = get_chat_model()
    briefing_message = model.invoke(prompt_value.to_messages())
    briefing_text = briefing_message.content

    print("=== Leadership Briefing ===")
    print(briefing_text)

    store_briefing(briefing_text, supplier_id)


if __name__ == "__main__":
    main()
