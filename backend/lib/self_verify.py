"""Self-verification loop (LifeMarkAI / Lovable parity)."""
from __future__ import annotations
import os, json, asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

REQUIRED_HINTS = ["package.json", "src/main.tsx", "src/App.tsx", "index.html"]

def static_smoke(project_path: Path) -> Dict[str, Any]:
    issues, present = [], []
    for name in REQUIRED_HINTS:
        p = project_path / name
        if p.exists():
            present.append(name)
        else:
            issues.append(f"missing:{name}")
    pkg = project_path / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            deps = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}
            if "react" not in deps:
                issues.append("package.json: react dependency missing")
            if "vite" not in deps:
                issues.append("package.json: vite missing")
        except json.JSONDecodeError:
            issues.append("package.json: invalid JSON")
    app = project_path / "src" / "App.tsx"
    if app.exists() and len(app.read_text(encoding="utf-8").strip()) < 40:
        issues.append("src/App.tsx looks empty or stub-only")
    return {"ok": len(issues) == 0, "method": "static", "present": present, "issues": issues}

async def preview_http_smoke(preview_url: str, timeout: float = 8.0) -> Dict[str, Any]:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(preview_url)
            body = r.text[:2000]
            issues = []
            if r.status_code >= 400:
                issues.append(f"http_{r.status_code}")
            if "Failed to compile" in body or "SyntaxError" in body:
                issues.append("compile_error_in_body")
            if len(body.strip()) < 20:
                issues.append("empty_body")
            return {"ok": len(issues) == 0, "method": "http", "status": r.status_code, "issues": issues}
    except Exception as e:
        return {"ok": False, "method": "http", "issues": [f"fetch_error:{type(e).__name__}"]}

async def playwright_smoke(preview_url: str) -> Dict[str, Any]:
    if os.environ.get("PLAYWRIGHT_ENABLED", "").lower() not in ("1", "true", "yes"):
        return {"ok": True, "method": "playwright", "skipped": True, "issues": []}
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return {"ok": True, "method": "playwright", "skipped": True, "issues": ["playwright_not_installed"]}
    console_errors, page_errors = [], []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            await page.goto(preview_url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1.5)
            root = await page.query_selector("#root")
            empty_root = False
            if root:
                text = (await root.inner_text()) or ""
                empty_root = len(text.strip()) == 0
            await browser.close()
            issues = [f"console:{e[:120]}" for e in console_errors[:5]] + [f"pageerror:{e[:120]}" for e in page_errors[:5]]
            if empty_root:
                issues.append("empty_root")
            return {"ok": len(issues) == 0, "method": "playwright", "issues": issues}
    except Exception as e:
        return {"ok": False, "method": "playwright", "issues": [f"playwright_error:{type(e).__name__}:{e}"]}

async def verify_project(project_path: Path, preview_url: Optional[str] = None) -> Dict[str, Any]:
    static = static_smoke(project_path)
    http_result = pw_result = None
    if preview_url:
        http_result = await preview_http_smoke(preview_url)
        pw_result = await playwright_smoke(preview_url)
    all_issues = list(static.get("issues") or [])
    if http_result:
        all_issues.extend(http_result.get("issues") or [])
    if pw_result and not pw_result.get("skipped"):
        all_issues.extend(pw_result.get("issues") or [])
    return {"ok": len(all_issues) == 0, "static": static, "http": http_result, "playwright": pw_result, "issues": all_issues}
