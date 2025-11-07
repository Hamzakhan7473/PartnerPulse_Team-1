# LangChain Integration Examples

This directory showcases how to plug MemMachine into LangChain agents by
implementing the ``BaseChatMessageHistory`` interface. Use these helpers to give
LangChain workflows durable, session-aware memory backed by MemMachine's
episodic store.

## Files

- `memmachine_memory.py` – Chat history adapter that persists conversations via
  the MemMachine REST API. It can optionally hydrate previous interactions so
  that each LangChain session starts with the same context used by the supplier
  demo.
- `demo_conversation.py` – Minimal command-line chat loop that wires the adapter
  into a `RunnableWithMessageHistory` chain using `ChatOpenAI`.

## Quick Start

1. Ensure the MemMachine stack is running (see the project README for Docker
   compose instructions). The default demo expects the API on
   `http://localhost:8080`.
2. Install LangChain packages inside the repo's virtual environment:

   ```bash
   source .venv/bin/activate
   pip install langchain-core langchain-openai
   ```

3. Set your OpenAI key so the sample chain can generate responses:

   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

4. Run the console demo:

   ```bash
   python examples/langchain/demo_conversation.py
   ```

   Every exchange is written to MemMachine. You can inspect the resulting
   episodic entries through the supplier frontend's new Memory Timeline.

## Using the Adapter in Your Own Chains

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from examples.langchain.memmachine_memory import MemMachineChatMessageHistory

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

chain = prompt | ChatOpenAI(model="gpt-4.1-mini")

runnable = RunnableWithMessageHistory(
    chain,
    lambda cfg: MemMachineChatMessageHistory(session_id=cfg["configurable"]["session_id"]),
    input_messages_key="input",
    history_messages_key="chat_history",
)

runnable.invoke({"input": "How did our last supplier meeting go?"}, config={"configurable": {"session_id": "my-demo"}})
```

The adapter automatically posts each LangChain message to `POST /v1/memories/episodic`
and includes basic metadata so it shows up alongside episodic events captured by
the Amazon supplier experience.

## Features at a glance
- **Durable chat history** – MemMachine becomes the single source of truth for LangChain conversations, keeping episodic memory aligned even across restarts.
- **Session hydration** – Optional history loading lets chains resume with prior context, matching the supplier demo’s multi-session behavior.
- **Deployment-ready API usage** – Uses the same REST endpoints your agents already rely on (`/v1/memories/episodic`, `/v1/memories/search`, `/v1/memories/episodic/clear`).
- **Metadata-aware memories** – Stores message type (`human`, `assistant`, `system`) so MemMachine’s rerankers and timelines can visualize who said what.
- **Composable architecture** – Plug into any LangChain `RunnableWithMessageHistory`, agent, or evaluation harness without rewriting memory logic.
- **Persona prompts** – `demo_conversation.py` dynamically selects system prompts for sales, operations, and manager personas (or defaults to a generic assistant).
- **Replay buffers** – Specify `history_limit` to hydrate the last _n_ messages from MemMachine before generating new responses.
- **CLI helper** – `run_profile.py` runs a single question for any persona from the command line; perfect for scripted demos.

## Role-based quick start (“Select Your Role”)

Choose the persona you want to simulate and use the corresponding `session_id`. Each role keeps its own MemMachine history so the supplier dashboard can highlight differences between teams.

| Role | Purpose | Session ID suggestion |
| --- | --- | --- |
| Sales Personnel | Focus on relationship-building notes, follow-ups, pricing negotiations. | `profile_sales` |
| Operations & Logistics | Track delivery performance, inventory, and escalation history. | `profile_ops` |
| Supplier Account Manager | Monitor strategic health, analytics, and cross-functional insights. | `profile_manager` |

### 1. Run the LangChain demo for your role

```bash
python examples/langchain/demo_conversation.py
```

Edit the `session_id` near the bottom of `demo_conversation.py` (or supply it via code) to match the role you picked, for example:

```python
session_id = "profile_sales"
```

Chat with the assistant (`You: ...`). Every exchange is stored in MemMachine under that role’s session.

### 2. Repeat for the other roles

Change `session_id` to `profile_ops` and then `profile_manager`, rerun the script, and ask the types of questions each persona would care about (e.g., delivery issues for Ops, analytics summaries for the Manager).

### 3. Inspect results in the supplier UI

- Open `http://localhost:3000` (React dev server) → query “Tell me about supplier SUP-101”.
- Check the **Memory Timeline** to see separate entries tagged with each session.

### 4. Programmatic usage example

```python
from demo_conversation import conversation_chain, resolve_system_prompt

profiles = {
    "profile_sales": "Summarize negotiations and next steps.",
    "profile_ops": "Highlight recent delivery incidents.",
    "profile_manager": "Provide analytics view of supplier SUP-101.",
}

chain = conversation_chain()

for session_id, prompt in profiles.items():
    chain.with_config(configurable={"session_id": session_id, "history_limit": 5}).invoke(
        {"input": prompt, "system_prompt": resolve_system_prompt(session_id)}
    )
```

After the loop, each role will have a dedicated memory trail in MemMachine and the supplier frontend.

### 5. One-off CLI helper

```bash
python examples/langchain/run_profile.py --profile profile_ops \
  --history-limit 5 \
  "Flag any logistics risks for supplier SUP-202."
```

The script prints the persona’s answer and persists the exchange to MemMachine so it immediately shows up in the React timeline.

### 6. Multi-persona leadership briefing

```bash
python examples/langchain/aggregated_briefing.py SUP-202 --history-limit 5
```

This orchestrates the Sales, Ops, and Manager personas, then synthesizes a leadership briefing and stores it under the `profile_leadership` session in MemMachine.

### 7. Retrieval QA powered by MemMachine

```bash
python examples/langchain/retrieval_qa_demo.py \
  "What logistics risks exist for supplier SUP-202?" \
  --session-id profile_ops
```

The custom retriever fetches episodic memories via the MemMachine REST API and feeds them into LangChain’s `RetrievalQA` chain so answers are grounded in stored history.


