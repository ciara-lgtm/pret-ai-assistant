# Pret AI Assistant

This repository contains the initial project skeleton for a production-quality prototype called Pret AI Assistant.

## Proposed structure and purpose

- backend/: Python FastAPI service for the local prototype API. It keeps the application entry point, route layer, services, and models separated so future business logic can be added cleanly.
- backend/app/api/: API route declarations. This is where HTTP endpoints live, such as the health route.
- backend/app/services/: business-facing service layer. These modules encapsulate logic and remain independent from transport concerns.
- backend/app/models/: typed response and data models. This makes the API contract explicit and easy to extend.
- backend/tests/: automated tests for the backend layer.
- frontend/: React application for the Pret Employee Assistant chat UI. It calls the existing backend chat API through the Vite development proxy.
- data/knowledge/: placeholder for Pret knowledge, troubleshooting guidance, and reusable reference material.
- .env.example: environment variable template for local development without storing real secrets.
- .gitignore: excludes virtual environments, dependencies, build artifacts, caches, and editor settings.

## Current implementation

This version includes:
- a FastAPI app with a clean entry point
- a GET /health endpoint returning a simple JSON health response
- a POST /api/v1/chat endpoint
- local Markdown knowledge retrieval and the mock equipment-ticket workflow
- a Pret-branded React chat interface connected to the backend

## Clone the project

Replace `<repository-url>` with the repository's Git URL:

```bash
git clone <repository-url>
cd pret-ai-assistant
```

## Local run

### 1) Backend setup

Use Python 3.13 for this project. Python 3.14 can fail while building `pydantic-core`.

```cmd
cd pret-ai-assistant
uv venv --python 3.13 --seed .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### 2) Configure Azure/Foundry connection

Create a local `.env` file from `.env.example` and provide the real values for your Microsoft Foundry deployment.

```env
USE_FAKE_AI=false
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=pret-assistant-poc
```

Required values:
- `AZURE_OPENAI_ENDPOINT` — the Azure OpenAI resource endpoint
- `AZURE_OPENAI_API_KEY` — the API key for the resource
- `AZURE_OPENAI_DEPLOYMENT` — the deployment name, currently `pret-assistant-poc`
- `USE_FAKE_AI` — set to `false` to use the real provider; leave as `true` for local tests or fake-mode development

Do not commit real secrets. Keep `.env` local only.

### 3) Start the backend

For local development without Azure credentials, leave `USE_FAKE_AI=true` in `.env`.
The application loads `.env` automatically from the project root.

```cmd
cd pret-ai-assistant
.venv\Scripts\activate.bat
uvicorn app.main:app --app-dir backend --reload
```

The backend will run at:
- http://127.0.0.1:8000
- health check: http://127.0.0.1:8000/health

### 4) Run backend tests

```cmd
cd pret-ai-assistant
.venv\Scripts\activate.bat
python -m pytest backend/tests -q
```

### 5) Frontend setup and run

```cmd
cd pret-ai-assistant\frontend
npm install
npm run dev
```

The frontend runs at http://localhost:5173. During development, Vite proxies `/api` requests to the backend at http://127.0.0.1:8000.

Run the backend and frontend in separate terminals.

### Quick reminder

If the venv is missing or broken, recreate it with:

```cmd
cd pret-ai-assistant
rmdir /s /q .venv
uv venv --python 3.13 --seed .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

