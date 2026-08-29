# IncidentGraph

IncidentGraph is an AI-powered production incident investigation system.

It combines code intelligence, GitHub changes, observability data,
AWS infrastructure state, and previous incident history to investigate
production incidents and generate an evidence-backed Root Cause Analysis
(RCA).

The investigation is orchestrated using LangGraph.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      React UI         │
                         │   Vite + JavaScript   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Flask Backend     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      LangGraph       │
                         │    Orchestration     │
                         └──────────┬───────────┘
                                    │
                           ┌────────┴────────┐
                           │  LLM Reasoning  │
                           └────────┬────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌──────────────┐
       │ LatentGraph │       │   GitHub    │       │Observability │
       │ Code Intel. │       │   Changes   │       │Logs/Metrics/ │
       │             │       │ Deployments │       │    Traces    │
       └──────┬──────┘       └──────┬──────┘       └──────┬───────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                         ┌──────────▼───────────┐
                         │    AWS / Infra       │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │  Incident History    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     RCA Generator     │
                         └──────────────────────┘
```

Investigation Flow
A typical investigation looks like:

```
Incident
│
▼
Incident Trigger
│
▼
LLM Reasoning
│
├──► LatentGraph
│ │
│ └──► Code paths / files / dependencies
│
▼
LLM Reasoning
│
├──► GitHub
│ │
│ └──► Commits / PRs / deployments
│
▼
LLM Reasoning
│
├──► Observability
│ │
│ └──► Logs / metrics / traces
│
▼
LLM Reasoning
│
├──► AWS
│ │
│ └──► Infrastructure state
│
▼
LLM Reasoning
│
├──► Incident History
│ │
│ └──► Similar previous incidents
│
▼
RCA
```

The LLM does not directly execute arbitrary actions.
It produces a structured decision such as:
{
"next_action": "github",
"reason": "A recent deployment may explain the increase in errors.",
"query": "Find deployments and commits affecting payment-service.",
"hypothesis": "A recent deployment introduced the regression.",
"confidence": 72
}

LangGraph then routes execution to the selected node.

Project Structure
incidentgraph/
│
├── backend/
│ ├── app.py
│ ├── config.py
│ ├── Dockerfile
│ │
│ ├── api/
│ │ ├── incident_routes.py
│ │ ├── webhook_routes.py
│ │ └── health_routes.py
│ │
│ ├── agent/
│ │ ├── graph.py
│ │ ├── state.py
│ │ ├── router.py
│ │ ├── checkpoint.py
│ │ └── prompts.py
│ │
│ ├── nodes/
│ │ ├── incident_trigger.py
│ │ ├── reasoning.py
│ │ ├── latentgraph.py
│ │ ├── github.py
│ │ ├── observability.py
│ │ ├── aws_infra.py
│ │ ├── incident_history.py
│ │ └── rca.py
│ │
│ ├── integrations/
│ │ ├── latentgraph_client.py
│ │ ├── github_client.py
│ │ ├── aws_client.py
│ │ ├── observability_client.py
│ │ └── database.py
│ │
│ ├── services/
│ │ ├── normalization.py
│ │ └── incident_service.py
│ │
│ ├── models/
│ │ ├── database.py
│ │ └── schemas.py
│ │
│ └── db/
│ ├── connection.py
│ └── migrations/
│
├── frontend/
│ ├── Dockerfile
│ ├── index.html
│ ├── vite.config.js
│ ├── tailwind.config.js
│ ├── package.json
│ │
│ └── src/
│ ├── components/
│ ├── pages/
│ ├── services/
│ ├── assets/
│ ├── App.jsx
│ ├── main.jsx
│ └── styles.css
│
├── tests/
├── scripts/
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
└── README.md

Requirements

- Python 3.12+
- Node.js 22+
- Docker / Docker Compose
- PostgreSQL 16+
- OpenAI API key
- GitHub token
- AWS credentials
- LatentGraph / LatentCode access

Environment Setup
Create the environment file:
cp .env.example .env

Then configure:
OPENAI_API_KEY
GITHUB_TOKEN
AWS_REGION
AWS credentials
LATENTGRAPH_API_KEY
LGRAPH_PROJECT_ID
LGRAPH_BRANCH

Do not commit .env

Running With Docker
From the repository root: docker compose up --build

The services will be available at:
Frontend:
http://localhost:5173

Backend:
http://localhost:5000

Health:
http://localhost:5000/api/health

PostgreSQL:
localhost:5432

Running Backend Locally
Create a virtual environment: `python3.12 -m venv .venv`

Activate it: `source .venv/bin/activate`

Install dependencies: `pip install -r requirements.txt`

Start PostgreSQL and configure .env.
Initialize the database: python scripts/setup_db.py

Run the backend:

````

cd backend
python app.py

```


Running Frontend Locally
```

cd frontend
npm install
npm run dev

````

Seed Demo Data
After configuring the database: `python scripts/seed_demo.py`

This creates sample incidents for development and UI testing.

Starting an Investigation
Send:
POST /api/incidents
Content-Type: application/json
Example:
{
"service": "payment-service",
"problem": "Payment API error rate increased significantly",
"severity": "critical",
"timestamp": "2026-08-29T14:30:00Z",
"repository": "acme/payment-service",
"source": "manual"
}
The backend initializes the LangGraph state and starts the investigation.

Investigation State
LangGraph maintains a shared state containing information such as:
incident
current_step
next_action
investigation_history
findings
evidence
hypotheses
code_context
github_changes
observability_data
infrastructure_state
historical_findings
affected_components
confidence
final_rca
errors

Each node reads the state and returns additional information.

Data Storage
PostgreSQL stores:

- Incidents
- Investigation summaries
- Evidence
- Affected components
- Recommended fixes
  LangGraph checkpointing can additionally persist the agent state.
  External systems remain the source of truth for their respective data:
  GitHub → GitHub
  AWS → AWS
  Logs → CloudWatch
  Metrics → CloudWatch
  Traces → X-Ray
  Code graph → LatentGraph

IncidentGraph retrieves the information required for an investigation
and correlates it rather than attempting to replace those systems.

Safety Model
The investigation integrations are intended to be read-only.
IncidentGraph does not automatically:

- modify source code
- merge pull requests
- deploy applications
- restart infrastructure
- delete resources
- modify AWS configuration
  The initial system is designed for investigation and RCA generation.

Testing
Run: `pytest`
Run with verbose output: `pytest -v`
The tests cover:

- Incident state initialization
- LangGraph routing
- Reasoning-node decisions
- RCA generation
- GitHub integration behavior
- Database models
- Normalization utilities
