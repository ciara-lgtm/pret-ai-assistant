# Pret AI Assistant

This repository contains the initial project skeleton for a production-quality prototype called Pret AI Assistant.

## Proposed structure and purpose

- backend/: Python FastAPI service for the local prototype API. It keeps the application entry point, route layer, services, and models separated so future business logic can be added cleanly.
- backend/app/api/: API route declarations. This is where HTTP endpoints live, such as the health route.
- backend/app/services/: business-facing service layer. These modules encapsulate logic and remain independent from transport concerns.
- backend/app/models/: typed response and data models. This makes the API contract explicit and easy to extend.
- backend/tests/: automated tests for the backend layer.
- frontend/: React application shell for the prototype UI. It contains the chat interface and supporting components without any AI functionality yet.
- data/knowledge/: placeholder for Pret knowledge, troubleshooting guidance, and reusable reference material.
- .env.example: environment variable template for local development without storing real secrets.
- .gitignore: excludes virtual environments, dependencies, build artifacts, caches, and editor settings.

## Current implementation

This initial version includes:
- a FastAPI app with a clean entry point
- a GET /health endpoint returning a simple JSON health response
- a basic pytest health test
- a React app that renders a placeholder chat interface
- a minimal, extensible project structure ready for future feature work

## Local run

### 1) Backend setup

Use Python 3.13 for this project. Python 3.14 can fail while building `pydantic-core`.

```cmd
cd /d "C:\Users\alexh\OneDrive\Documents\Ciara jobs\Pret-AI-Assistant\pret-ai-assistant"
uv venv --python 3.13 --seed .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### 2) Start the backend

```cmd
cd /d "C:\Users\alexh\OneDrive\Documents\Ciara jobs\Pret-AI-Assistant\pret-ai-assistant"
.venv\Scripts\activate.bat
uvicorn app.main:app --app-dir backend --reload
```

The backend will run at:
- http://127.0.0.1:8000
- health check: http://127.0.0.1:8000/health

### 3) Run backend tests

```cmd
cd /d "C:\Users\alexh\OneDrive\Documents\Ciara jobs\Pret-AI-Assistant\pret-ai-assistant"
.venv\Scripts\activate.bat
python -m pytest backend/tests -q
```

### 4) Frontend setup and run

```cmd
cd /d "C:\Users\alexh\OneDrive\Documents\Ciara jobs\Pret-AI-Assistant\pret-ai-assistant\frontend"
npm install
npm run dev -- --host 0.0.0.0
```

The frontend will run in the terminal output shown by Vite, usually on a local port such as http://localhost:5173.

### Quick reminder

If the venv is missing or broken, recreate it with:

```cmd
cd /d "C:\Users\alexh\OneDrive\Documents\Ciara jobs\Pret-AI-Assistant\pret-ai-assistant"
rmdir /s /q .venv
uv venv --python 3.13 --seed .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

