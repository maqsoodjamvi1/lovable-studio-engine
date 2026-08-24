#!/bin/bash
# Finish push of remaining large files via GitHub API
# Requires: GITHUB_TOKEN or gh auth login
set -euo pipefail
OWNER=maqsoodjamvi1
REPO=lovable-studio-engine
BRANCH=main
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

upload() {
  local path="$1"
  local msg="$2"
  echo "→ $path"
  local sha
  sha=$(curl -s -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    "https://api.github.com/repos/$OWNER/$REPO/contents/$path?ref=$BRANCH" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sha',''))" 2>/dev/null || true)
  local b64
  b64=$(base64 -w0 "$path")
  local body
  if [ -n "$sha" ]; then
    body=$(python3 -c "import json; print(json.dumps({'message':'''$msg''','branch':'''$BRANCH''','content':'''$b64''','sha':'''$sha'''}))")
  else
    body=$(python3 -c "import json; print(json.dumps({'message':'''$msg''','branch':'''$BRANCH''','content':'''$b64'''}))")
  fi
  curl -s -X PUT -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "https://api.github.com/repos/$OWNER/$REPO/contents/$path" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content',{}).get('path','ERR'), d.get('commit',{}).get('sha','')[:7])"
}

for f in \
  backend/lib/connectors.py \
  backend/lib/deploy.py \
  backend/lib/self_verify.py \
  backend/orchestrator.py \
  frontend/src/WorkspaceDashboard.tsx \
  frontend/src/ProjectSelector.tsx \
  shared/canvas-injector.js \
  scripts/provision_project.py \
  docker/Dockerfile.backend \
  docker/Dockerfile.frontend \
  docker/docker-compose.dev.yml \
  docker/nginx.conf
do
  [ -f "$f" ] && upload "$f" "v3: $f"
done
echo "All remaining files uploaded."
