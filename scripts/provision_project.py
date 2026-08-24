#!/usr/bin/env python3
"""
Standalone provisioning helper (mirrors orchestrator._write_scaffold_files).
Creates a new isolated workspace + Git repo + optional Postgres tenant DB
with auth card, Navbar, Postgres client stub, and optional FastAPI backend.
"""

import os
import sys
import subprocess
import uuid
from pathlib import Path

WORKSPACE_BASE = Path(os.environ.get("WORKSPACE_DIR", "/var/platform/workspaces"))
POSTGRES_CONTAINER = os.environ.get("POSTGRES_CONTAINER", "production-postgres")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")


def provision_new_project_sandbox(project_id: str, project_name: str = "New Project"):
    project_path = WORKSPACE_BASE / project_id
    if project_path.exists():
        print(f"⚠️  Project {project_id} already exists at {project_path}")
        return project_path

    project_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created workspace {project_path}")

    subprocess.run(["git", "init", str(project_path)], check=True)
    subprocess.run(
        ["git", "-C", str(project_path), "config", "user.name", "PaaS-Agent-Core"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project_path), "config", "user.email", "agent@platform.internal"],
        check=True,
    )

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
        from orchestrator import _write_scaffold_files

        _write_scaffold_files(project_path)
        print("✅ Rich scaffold written via orchestrator helper")
    except Exception as e:
        print(f"ℹ️  Falling back to minimal scaffold ({e})")
        src = project_path / "src"
        src.mkdir(exist_ok=True)
        (src / "App.tsx").write_text(
            'export default function App() {\n  return <div className="p-8 text-white">Hello Sandbox</div>;\n}\n',
            encoding="utf-8",
        )
        (src / "main.tsx").write_text(
            'import React from "react";\nimport ReactDOM from "react-dom/client";\nimport App from "./App";\nimport "./index.css";\nReactDOM.createRoot(document.getElementById("root")!).render(<App />);\n',
            encoding="utf-8",
        )
        (src / "index.css").write_text(
            "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n",
            encoding="utf-8",
        )
        (project_path / "index.html").write_text(
            '<!DOCTYPE html><html><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>\n',
            encoding="utf-8",
        )
        (project_path / "package.json").write_text(
            '{"name":"sandbox-app","private":true,"version":"0.0.0","type":"module","scripts":{"dev":"vite --host 0.0.0.0"},"dependencies":{"react":"^18.3.1","react-dom":"^18.3.1"},"devDependencies":{"@vitejs/plugin-react":"^4.3.1","vite":"^5.4.2","tailwindcss":"^3.4.10","typescript":"^5.5.4"}}\n',
            encoding="utf-8",
        )

    subprocess.run(["git", "-C", str(project_path), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(project_path), "commit", "-m", "initial_boilerplate_checkpoint"],
        check=True,
    )

    safe_db = f"app_{project_id.replace('-', '_')}"
    try:
        subprocess.run(
            f"docker exec {POSTGRES_CONTAINER} psql -U {POSTGRES_USER} "
            f"-c 'CREATE DATABASE {safe_db};'",
            shell=True,
            check=True,
            capture_output=True,
        )
        print(f"📦 Database {safe_db} created.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  Postgres container not available – skipped tenant DB creation.")

    print(f"🚀 Project '{project_name}' ({project_id}) is ready for AI prompts.")
    return project_path


if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else str(uuid.uuid4())
    name = sys.argv[2] if len(sys.argv) > 2 else "New Project"
    provision_new_project_sandbox(pid, name)
