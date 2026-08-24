"""Connector registry + proxy (LifeMarkAI / Lovable parity)."""
from __future__ import annotations
import os, re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import httpx

CONNECTOR_REGISTRY: Dict[str, Dict[str, Any]] = {
    "openai": {"name": "OpenAI", "base_url": "https://api.openai.com", "auth_env": "OPENAI_API_KEY", "auth_header": "Authorization", "auth_prefix": "Bearer ", "paths_allow": [r"^/v1/"]},
    "stripe": {"name": "Stripe", "base_url": "https://api.stripe.com", "auth_env": "STRIPE_SECRET_KEY", "auth_header": "Authorization", "auth_prefix": "Bearer ", "paths_allow": [r"^/v1/"]},
    "resend": {"name": "Resend", "base_url": "https://api.resend.com", "auth_env": "RESEND_API_KEY", "auth_header": "Authorization", "auth_prefix": "Bearer ", "paths_allow": [r"^/"]},
    "github": {"name": "GitHub", "base_url": "https://api.github.com", "auth_env": "GITHUB_TOKEN", "auth_header": "Authorization", "auth_prefix": "Bearer ", "paths_allow": [r"^/"]},
    "slack": {"name": "Slack", "base_url": "https://slack.com/api", "auth_env": "SLACK_BOT_TOKEN", "auth_header": "Authorization", "auth_prefix": "Bearer ", "paths_allow": [r"^/"]},
    "linear": {"name": "Linear", "base_url": "https://api.linear.app", "auth_env": "LINEAR_API_KEY", "auth_header": "Authorization", "auth_prefix": "", "paths_allow": [r"^/graphql"]},
    "notion": {"name": "Notion", "base_url": "https://api.notion.com", "auth_env": "NOTION_API_KEY", "auth_header": "Authorization", "auth_prefix": "Bearer ", "paths_allow": [r"^/v1/"]},
    "sendgrid": {"name": "SendGrid", "base_url": "https://api.sendgrid.com", "auth_env": "SENDGRID_API_KEY", "auth_header": "Authorization", "auth_prefix": "Bearer ", "paths_allow": [r"^/v3/"]},
}

def list_connectors() -> List[Dict[str, Any]]:
    return [{"id": cid, "name": meta["name"], "base_url": meta["base_url"], "auth_env": meta["auth_env"], "configured": bool(os.environ.get(meta["auth_env"]))} for cid, meta in CONNECTOR_REGISTRY.items()]

def _path_allowed(path: str, patterns: List[str]) -> bool:
    return any(re.match(pat, path) for pat in patterns)

async def proxy_request(connector_id: str, method: str, path: str, *, query=None, body=None, extra_headers=None, project_env=None):
    meta = CONNECTOR_REGISTRY.get(connector_id)
    if not meta:
        return {"ok": False, "error": f"unknown_connector:{connector_id}"}
    if not path.startswith("/"):
        path = "/" + path
    if not _path_allowed(path, meta.get("paths_allow") or [r"^/"]):
        return {"ok": False, "error": "path_not_allowed"}
    env_source = {**os.environ, **(project_env or {})}
    token = env_source.get(meta["auth_env"], "")
    if not token:
        return {"ok": False, "error": f"missing_secret:{meta['auth_env']}"}
    url = meta["base_url"].rstrip("/") + path
    headers = {meta["auth_header"]: f"{meta.get('auth_prefix', '')}{token}", "Content-Type": "application/json", **(extra_headers or {})}
    parsed = urlparse(url)
    if parsed.hostname != urlparse(meta["base_url"]).hostname:
        return {"ok": False, "error": "host_mismatch"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.request(method.upper(), url, params=query, json=body, headers=headers)
            try:
                data = r.json()
            except Exception:
                data = {"raw": r.text[:4000]}
            return {"ok": r.status_code < 400, "status": r.status_code, "data": data}
    except Exception as e:
        return {"ok": False, "error": f"proxy_error:{type(e).__name__}:{e}"}

def system_prompt_block() -> str:
    ids = ", ".join(CONNECTOR_REGISTRY.keys())
    return f"\n### Connector proxy\nAvailable: {ids}\nPOST /api/connectors/{{id}}/proxy with method/path/body. Never put secrets in frontend.\n"
