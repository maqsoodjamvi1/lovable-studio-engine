# Lovable Studio Engine v3

Self-hosted AI app builder inspired by **Lovable** and [LifeMarkAI](https://github.com/maqsoodjamvi1/lifemarkai).
Zero vendor lock-in · Vanilla Postgres · Plan / Agent / Build modes.

**GitHub:** https://github.com/maqsoodjamvi1/lovable-studio-engine

## Features

| Feature | Status |
|---------|--------|
| Plan → approve → multi-file | ✅ |
| ReAct Agent mode | ✅ `/api/project/agent` |
| Self-verify (static + HTTP + Playwright) | ✅ |
| Connector proxy (8 services) | ✅ |
| One-click Publish | ✅ |
| Visual edits (text / className) | ✅ |
| Git + schema Time-Travel | ✅ |
| Auth + Postgres scaffold | ✅ |

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set ANTHROPIC_API_KEY
export WORKSPACE_DIR=$(pwd)/../workspaces BACKUP_DIR=$(pwd)/../backups
mkdir -p "$WORKSPACE_DIR" "$BACKUP_DIR"
uvicorn orchestrator:app --reload --port 8000

cd ../frontend && npm install && npm run dev
```

Open http://localhost:3000

## Modes

- **Build** — generate + self-heal + auto-verify
- **Plan** — structured plan, then approve & execute
- **Agent** — multi-step ReAct loop
- **Visual** — click element, edit text/class without full LLM
- **Self-verify / Publish** — smoke test and static deploy

## Sync large files

If `backend/orchestrator.py` or `frontend/src/WorkspaceDashboard.tsx` are missing:

```bash
export GITHUB_TOKEN=ghp_your_token
bash scripts/finish_github_push.sh
```

## Stack

FastAPI + Anthropic Claude · React + Vite + Tailwind · Vanilla Postgres · Docker/Coolify ready
