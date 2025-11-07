"""Minimal LangChain chat demo persisting history to MemMachine."""

from __future__ import annotations

import os
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

try:
    from langchain_openai import ChatOpenAI
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit(
        "langchain-openai is required for the demo. Install with `pip install langchain-openai`."
    ) from exc

from memmachine_memory import MemMachineChatMessageHistory

PERSONA_PROMPTS: dict[str, str] = {
    "profile_sales": (
        "You are a proactive sales specialist focusing on relationship status,"
        " follow-ups, pricing negotiations, and revenue opportunities."
    ),
    "profile_ops": (
        "You are an operations and logistics analyst monitoring supply chain"
        " risks, delivery incidents, and inventory stability."
    ),
    "profile_manager": (
        "You are a supplier account manager preparing briefings for leadership"
        " with strategic insights, risk summaries, and next steps."
    ),
}

DEFAULT_SYSTEM_PROMPT = "You are a supplier success assistant that leverages stored context."


def resolve_system_prompt(session_id: str) -> str:
    return PERSONA_PROMPTS.get(session_id, DEFAULT_SYSTEM_PROMPT)


def get_chat_model() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set the OPENAI_API_KEY environment variable before running the demo.")

    return ChatOpenAI(model="gpt-4.1-mini", temperature=0.2)


def conversation_chain(default_session_id: str = "langchain-demo-session", history_limit: int = 5) -> RunnableWithMessageHistory:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    model = get_chat_model()
    chain = prompt | model

    def history_factory(config: dict) -> MemMachineChatMessageHistory:
        if isinstance(config, str):  # pragma: no cover - defensive
            session_id = config or default_session_id
            limit = history_limit
        else:
            cfg = config.get("configurable", {}) if isinstance(config, dict) else {}
            session_id = cfg.get("session_id", default_session_id)
            limit = cfg.get("history_limit", history_limit)

        history = MemMachineChatMessageHistory(
            session_id=session_id,
            load_remote_history=True,
        )
        history.pull(limit=limit)
        return history

    return RunnableWithMessageHistory(
        chain,
        history_factory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )


def main() -> None:
    session_id = input(
        "Enter session/profile id (default: supplier-demo): "
    ).strip() or "supplier-demo"

    try:
        history_limit = int(
            input("Number of recent messages to hydrate (default: 5): ").strip() or 5
        )
    except ValueError:
        history_limit = 5

    chain = conversation_chain(
        default_session_id=session_id,
        history_limit=history_limit,
    )

    print(
        f"MemMachine LangChain demo (session: {session_id}, history_limit={history_limit})"
        "\nType 'quit' to exit.\n"
    )

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input.strip() or user_input.strip().lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        response = chain.invoke(
            {
                "input": user_input,
                "system_prompt": resolve_system_prompt(session_id),
            },
            config={
                "configurable": {
                    "session_id": session_id,
                    "history_limit": history_limit,
                }
            },
        )
        print(f"Assistant: {response.content}\n")


if __name__ == "__main__":
    main()


