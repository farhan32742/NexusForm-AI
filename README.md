
# 🚀 Agentic AI - Dynamic Data Entry System
### *State-of-the-Art LangGraph Orchestration with HITL & MCP*

## 📌 Project Overview
This project is an industrial-grade Agentic AI system designed to automate complex form-filling processes. Unlike static chatbots, this system dynamically "scouts" backend API requirements, extracts data from natural language, validates it using strict logic, and enforces **Human-in-the-Loop (HITL)** oversight before submitting data via the **Model Context Protocol (MCP)**.

The system is built for resilience, utilizing **PostgreSQL** for persistent memory, ensuring no progress is lost even if the server restarts.

---

## 🏗️ Architecture: The Brain & The Muscle

The system is divided into two distinct logical layers:

1.  **The Brain (Agent App):** Powered by **LangGraph** and **OpenAI GPT-4o-mini**. It handles reasoning, conversation management, and state persistence.
2.  **The Muscle (MCP Server):** A decoupled **Model Context Protocol** server that handles the actual "action"—securely communicating with the MySQL backend to save records.

---

## 🛠️ Key Features

*   **Dynamic Discovery (Scout Node):** Automatically parses OpenAPI/Swagger specifications to understand form requirements (Data types, Required fields, Regex patterns).
*   **Deep Recursive Validation:** An Inspector node that validates nested objects (like `items` or `quotebasicinfo`) to ensure 100% data integrity.
*   **Persistent Transactional Memory:** Uses `PostgresSaver` to maintain an auditable state of every conversation turn.
*   **Human-in-the-Loop (HITL):** A physical breakpoint in the workflow that pauses the machine, providing a summary for human approval/editing before any API write happens.
*   **Secure Submissions:** Utilizes JWT-authorized requests and MCP tool isolation.

---

## 📂 Project Structure

```text
project-root/
├── apps/agent_app/                 # The LangGraph Orchestrator
│   ├── src/agenticAI_full_workflow/
│   │   ├── agent/                  # Workflow (StateGraph) definition
│   │   ├── project_nodes/          # Logic nodes (Scout, Agent, Inspector, etc.)
│   │   ├── agent_state/            # TypedDict state & Persistence
│   │   ├── utils/                  # API Loaders & DB Management
│   │   └── schemas/                # Dynamic Pydantic Models
│   ├── app.py                      # Production Entry Point (CLI)
│   └── .env                        # Configuration (Secrets)
├── mcp_servers/verification_mcp/   # The Action Layer
│   ├── src/server.py               # FastMCP Server
│   └── src/tools/                  # DB Handlers
├── shared_core/                    # Cross-cutting concerns (Logs/Exceptions)
└── docker-compose.yaml             # Containerization setup
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
*   Python 3.10+
*   PostgreSQL Instance (Local or Remote)
*   OpenAI API Key
*   `uv` (Recommended package manager)

### 2. Environment Configuration (`.env`)
Create a `.env` file in `apps/agent_app/`:
```env
# API Links
FORM_GET_SCHEMA_URL=https://testppapi.mspl.pk/quote/swagger/v2/swagger.json
FORM_SUBMIT_URL=https://testppapi.mspl.pk/quote/API/Price/GetPrice2

# Authentication
JWT_TOKEN=your_company_jwt_here

# AI Configuration
OPENAI_API_KEY=sk-xxxx
LANGSMITH_API_KEY=lsv2_xxxx # Optional for tracing

# Database (Postgres Persistence)
POSTGRES_URL=postgresql://postgres:password@127.0.0.1:5432/agent_db
```

### 3. Install Dependencies
```bash
uv sync
```

---

## 🎮 Workflow Execution

### The Workflow Loop:
1.  **Scout Node:** Hits the Swagger URL (with JWT) and builds a map of the required form.
2.  **Agent Node:** Listens to user input and extracts data into a JSON structure.
3.  **Inspector Node:** Performs a "Deep Check." If `Pickup Zip Code` is missing inside `quotebasicinfo`, it flags it.
4.  **Interviewer Node:** Friendly conversation to ask the user for missing/invalid data.
5.  **Review Gate (INTERRUPT):** Pauses the graph. The system displays a summary table.
6.  **Approval:**
    *   If user says **"Yes"**: Manually update state to `is_approved: True` and resume.
    *   If user says **"No/Edit"**: Agent re-extracts the correction and loops back to validation.
7.  **Submitter Node:** Spawns the MCP Server subprocess to securely POST data to the company API.

### Running the System
```bash
# To run the full interactive CLI
uv run python apps/agent_app/app.py

# To run the test suite
uv run python apps/agent_app/test.py
```

---

## 🔒 Production Readiness (Windows Server 2019)

*   **Persistence:** The `AsyncPostgresSaver` ensures that if the server reboots, the agent resumes exactly at the **Review Gate**.
*   **Token Optimization:** Message history is automatically trimmed to the last 6 turns to minimize latency and OpenAI costs.
*   **Logging:** Centralized logging via `shared_core` monitors performance and error rates.
*   **Process Management:** It is recommended to use **NSSM** or **Docker** to run the Python application as a background service on Windows Server 2019.

---

## 🛡️ Security Note
All PII (CNIC, Email, Phone) is handled within the memory of the specific `thread_id`. Ensure the PostgreSQL database is encrypted at rest and firewall rules only allow internal access to the DB port (5432).

---

**Developed for Industrial Data Entry Automation.**
*AI Engineer: FARHAN FAYAZ*