# Lovable Studio Engine v3

Self-hosted AI app builder inspired by **Lovable** and deep study of
[LifeMarkAI](https://github.com/maqsoodjamvi1/lifemarkai) — while keeping
**zero vendor lock-in** (vanilla Postgres, no forced Supabase).

## What LifeMarkAI taught us (and what we closed)

| Gap (vs LifeMarkAI / Lovable) | v3 status |
|-------------------------------|-----------|
| Self-verification after build | ✅ `/api/project/verify` |
| Connector gateway | ✅ `/api/connectors` + proxy |
| One-click publish | ✅ `/api/project/deploy` |
| Plan → approve → multi-file | ✅ |
| ReAct Agent mode | ✅ `/api/project/agent` |
| Visual edits | ✅ |
| Auth + Postgres scaffold | ✅ vanilla JWT |
| Time-travel Git + schema | ✅ |

## Quick start

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export WORKSPACE_DIR=$(pwd)/../workspaces BACKUP_DIR=$(pwd)/../backups
mkdir -p "$WORKSPACE_DIR" "$BACKUP_DIR"
uvicorn orchestrator:app --reload --port 8000

cd ../frontend && npm install && npm run dev
```

Repo: https://github.com/maqsoodjamvi1/lovable-studio-engine
