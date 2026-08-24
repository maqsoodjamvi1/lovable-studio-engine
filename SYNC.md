# Remaining large files

The full source lives in the project artifacts and local clone.

To finish syncing `backend/orchestrator.py` and `frontend/src/WorkspaceDashboard.tsx`:

```bash
# From a machine with the full repo copy:
git clone https://github.com/maqsoodjamvi1/lovable-studio-engine.git
cd lovable-studio-engine
# Copy from artifacts:
#   backend/orchestrator.py
#   frontend/src/WorkspaceDashboard.tsx
git add -A && git commit -m "v3: full orchestrator + WorkspaceDashboard" && git push
```

Or run:
```bash
export GITHUB_TOKEN=ghp_...
bash scripts/finish_github_push.sh
```

## Status
- [x] agent, connectors, deploy, self_verify
- [x] ProjectSelector, canvas-injector, provision, docker
- [x] Frontend shell, compose, README
- [ ] orchestrator.py (46KB) — use finish script
- [ ] WorkspaceDashboard.tsx (25KB) — use finish script
