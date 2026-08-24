"""One-click publish / deploy (LifeMarkAI / Lovable parity)."""
from __future__ import annotations
import os, json, shutil, subprocess
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone

def _run(cmd, cwd, timeout=180):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)

def try_vite_build(project_path: Path) -> Dict[str, Any]:
    if not (project_path / "node_modules").exists():
        inst = _run(["npm", "install", "--legacy-peer-deps"], project_path, timeout=300)
        if inst.returncode != 0:
            return {"ok": False, "stage": "npm_install", "stderr": (inst.stderr or "")[-2000:]}
    build = _run(["npm", "run", "build"], project_path, timeout=240)
    dist = project_path / "dist"
    if build.returncode != 0 or not dist.exists():
        return {"ok": False, "stage": "vite_build", "stderr": (build.stderr or build.stdout or "")[-2000:]}
    return {"ok": True, "dist": str(dist)}

def publish_project(project_id: str, project_path: Path, backup_dir: Path, *, public_base: Optional[str] = None) -> Dict[str, Any]:
    deploy_root = backup_dir / "deploys" / project_id
    deploy_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact = deploy_root / stamp
    build_result = try_vite_build(project_path)
    if build_result.get("ok"):
        shutil.copytree(build_result["dist"], artifact)
        method = "vite_static"
    else:
        artifact.mkdir(parents=True, exist_ok=True)
        for item in project_path.iterdir():
            if item.name in (".git", "node_modules", "dist", ".venv"):
                continue
            dest = artifact / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        method = "source_snapshot"
        build_result["fallback"] = True
    meta = {"project_id": project_id, "timestamp": stamp, "method": method, "build": build_result, "artifact": str(artifact)}
    (artifact / "deploy-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    webhook = os.environ.get("DEPLOY_WEBHOOK_URL")
    webhook_status = None
    if webhook:
        try:
            import httpx
            r = httpx.post(webhook, json={"project_id": project_id, "artifact": str(artifact), "method": method}, timeout=30.0)
            webhook_status = {"status": r.status_code, "body": r.text[:500]}
        except Exception as e:
            webhook_status = {"error": str(e)}
    base = public_base or os.environ.get("PUBLIC_APPS_BASE", "http://localhost:4173")
    url = f"{base.rstrip('/')}/{project_id}/{stamp}/"
    return {"status": "success", "method": method, "artifact": str(artifact), "url": url, "build_ok": bool(build_result.get("ok")), "webhook": webhook_status, "message": "Static build published." if build_result.get("ok") else "Source snapshot saved (build failed)."}
