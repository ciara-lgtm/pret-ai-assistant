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

### Backend

```bash
cd pret-ai-assistant
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

The application exposes the health endpoint at:
- GET /health

### Frontend

```bash
cd pret-ai-assistant/frontend
npm install
npm run dev -- --host 0.0.0.0
```

