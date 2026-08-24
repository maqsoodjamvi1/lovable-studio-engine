# Remaining large files

Full source is provided as compressed companions:

- `backend/orchestrator.py.gz.b64` (46KB source)
- `frontend/src/WorkspaceDashboard.tsx.gz.b64` (25KB source)

## Restore

```bash
python scripts/decode_large_files.py
```

This writes the full `.py` / `.tsx` next to the `.gz.b64` files.

## Alternative (token)

```bash
export GITHUB_TOKEN=ghp_...
bash scripts/finish_github_push.sh
```

## Status (v3)
- [x] agent, connectors, deploy, self_verify
- [x] ProjectSelector, canvas-injector, provision, docker
- [x] Frontend shell, compose, README
- [x] orchestrator.py + WorkspaceDashboard.tsx (via .gz.b64 + decode)
