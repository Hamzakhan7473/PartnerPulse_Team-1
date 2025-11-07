# MemMachine

<div align="center">

![Discord](https://img.shields.io/discord/1412878659479666810)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/MemMachine/MemMachine)
![GitHub License](https://img.shields.io/github/license/MemMachine/MemMachine)

</div>

## Universal memory layer for AI Agents

Meet MemMachine, an open-source memory layer for advanced AI agents. It enables
AI-powered applications to learn, store, and recall data and preferences from
past sessions to enrich future interactions. MemMachine's memory layer persists
across multiple sessions, agents, and large language models, building a
sophisticated, evolving user profile. It transforms AI chatbots into
personalized, context-aware AI assistants designed to understand and respond
with better precision and depth.

## Who Is MemMachine For?

- Developers building AI agents, assistants, or autonomous workflows.
- Researchers experimenting with agent architectures and cognitive models.

## Key Features

- **Multiple Memory Types:** MemMachine supports Working (Short Term),
    Persistent (Long Term), and Personalized (Profile) memory types.
- **Developer Friendly APIs:** Python SDK, RESTful, and MCP interfaces and
    endpoints to make integrating MemMachine easy into your Agents. For more
    information, refer to the
    [API Reference Guide](https://docs.memmachine.ai/api_reference).

## Architecture

1. Agents Interact via the API Layer
    Users interact with an agent, which connects to the MemMachine Memory core through a RESTful API, Python SDK, or MCP Server.
2. MemMachine Manages Memory
    MemMachine processes interactions and stores them in two distinct types: Episodic Memory for conversational context and Profile Memory for long-term user facts.
3. Data is Persisted to Databases
    Memory is persisted to a database layer where Episodic Memory is stored in a graph database and Profile Memory is stored in an SQL database.

<div align="center">

![MemMachine Architecture](https://github.com/MemMachine/MemMachine/blob/main/assets/img/MemMachine_Architecture.png)

</div>

## Use Cases & Example Agents

MemMachine's versatile memory architecture can be applied across any domain,
transforming generic bots into specialized, expert assistants. Our growing list
of [examples](examples/README.md) showcases the endless possibilities of
memory-powered agents that integrate into your own applications and solutions.

- **CRM Agent:** Your agent can recall a client's entire history and deal stage,
    proactively helping your sales team build relationships and close deals
    faster.
- **Healthcare Navigator:** Offer continuous patient support with an agent that
    remembers medical history and tracks treatment progress to provide a
    seamless healthcare journey.
- **Personal Finance Advisor:** Your agent will remember a user's portfolio and
    risk tolerance, delivering personalized financial insights based on their
    complete history.
- **Content Writer:** Build an assistant that remembers your unique style guide
    and terminology, ensuring perfect consistency across all documentation.

We're excited to see what you're working on. Join the
[Discord Server](https://discord.gg/usydANvKqD) and drop a shout-out to your
project in the **showcase** channel.

## Quick Start

Want to get started right away? Check out our
[Quick Start Guide](https://docs.memmachine.ai).

## Hackathon Demo Blueprint

This repository now contains a full end-to-end demo that combines the MemMachine
stack, a supplier FastAPI service, a React dashboard, and LangChain personas.

**Architecture (textual)**

```
┌─────────────────────────────┐
│ React Supplier Dashboard    │  ──▶  Displays health panel, quick prompts,
│ (examples/amazon_suppliers) │       and the Memory Timeline fed by MemMachine
└─────────────▲───────────────┘
              │ REST
┌─────────────┴───────────────┐
│ Supplier FastAPI Service    │  ──▶  /supplier/ingest, /supplier/query and /health
│ (examples/amazon_suppliers) │       routes orchestrate episodic/profile updates
└─────────────▲───────────────┘
              │ REST
┌─────────────┴───────────────┐
│ MemMachine API (Docker)     │  ──▶  /v1/memories/*, /v1/agents/* endpoints
│  - Episodic → Neo4j         │       persist LangChain & supplier memories
│  - Profile  → Postgres      │
└─────────────▲───────────────┘
              │ LCEL / REST
┌─────────────┴───────────────┐
│ LangChain Personas & Tools  │
│  - run_profile.py           │  ──▶  Sales / Ops / Manager sessions
│  - aggregated_briefing.py   │       synthesise leadership briefings
│  - retrieval_qa_demo.py     │       answer questions via MemMachine retriever
└─────────────────────────────┘
```

### Live demo flow

```bash
# 1) Start MemMachine infrastructure
./memmachine-compose.sh

# 2) Supplier backend (REST + LangChain-ready API)
cd examples/amazon_suppliers
source ../../.venv/bin/activate && source ../../.env
POSTGRES_HOST=localhost POSTGRES_PORT=55432 POSTGRES_USER=memmachine \
POSTGRES_PASSWORD=memmachine_password POSTGRES_DB=memmachine \
MEMORY_BACKEND_URL=http://localhost:8080 SUPPLIER_PORT=8001 \
SUPPLIER_SERVER_URL=http://localhost:8001 MODEL_API_KEY=$OPENAI_API_KEY \
python supplier_server.py

# 3) React dashboard (optional but great for storytelling)
cd frontend/react-ui
npm run dev -- --host

# 4) LangChain personas
cd ../../langchain
source ../../.venv/bin/activate
export OPENAI_API_KEY=sk-...              # same key as in .env
python run_profile.py --profile profile_sales \
  "Summarize outstanding negotiations for supplier SUP-202."
python run_profile.py --profile profile_ops \
  "Flag any logistics risks for supplier SUP-202."
python run_profile.py --profile profile_manager \
  "Create a leadership briefing for supplier SUP-202."

# 5) Leadership briefing orchestrated from multiple personas
python aggregated_briefing.py SUP-202 --history-limit 5

# 6) Retrieval QA grounded in MemMachine memories
python retrieval_qa_demo.py \
  "What logistics risks exist for supplier SUP-202?" \
  --session-id profile_ops
```

Open `http://localhost:8080/docs` to highlight:

- `GET /v1/agents/{agent_id}/sessions` → shows LangChain session IDs
- `POST /v1/memories/search` → displays the episodic entries just generated

Then refresh `http://localhost:3000` to demonstrate the Memory Timeline and
System Status panel reflecting the same data.

## Future Scope

- **Multi-agent orchestration:** extend `aggregated_briefing.py` with additional
  personas (finance, procurement) and experiment with LangGraph for richer
  workflows.
- **Conflict & drift detection:** analyse episodic memories for contradictory
  statements or outdated facts, storing “alerts” back in MemMachine.
- **Vector hybrid search:** combine the MemMachine retriever with embedding
  indexes for semantic + keyword retrieval across long time spans.
- **UI launch actions:** wire the React dashboard to trigger LangChain personas
  via an endpoint so non-technical users can kick off automated briefings.
- **CI automation:** add pytest smoke tests that run the personas and assert the
  resulting sessions through the REST API to guard against regressions.

## Installation

MemMachine is distributed as a Docker container and Python package. For full
installation options, visit the [documentation](https://docs.memmachine.ai).

## Basic Usage

Get started with a simple "Hello World" example by following the
[Quick Start Guide](https://docs.memmachine.ai/getting_started/quickstart).

## Documentation

- [Main Website](https://memmachine.ai)
- [Docs & API Reference](https://docs.memmachine.ai)

## Community & Support

- **Discord:** Join our Docker community for support, updates, and discussions:
    [https://discord.gg/usydANvKqD](https://discord.gg/usydANvKqD)
- **Issues & Feature Requests:** Use GitHub
    [Issues](https://github.com/MemMachine/MemMachine/issues).

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines.

## License

MemMachine is released under the [Apache 2.0 License](LICENSE).
