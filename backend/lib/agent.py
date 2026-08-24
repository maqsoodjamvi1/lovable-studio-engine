"""
ReAct-style agent loop (LifeMarkAI / Lovable Agent mode parity).

Observe → Think → Act → Observe, with a fixed max step budget.
Acts = generate/heal files via the same Claude path as the orchestrator.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable

AGENT_SYSTEM = """
You are an autonomous coding agent operating in ReAct style.
For each step respond with ONLY valid JSON:
{
  "thought": "brief reasoning",
  "action": "write_file" | "read_file" | "list_files" | "done" | "verify",
  "path": "src/...",          // for write_file / read_file
  "content": "...",           // for write_file — full file content
  "summary": "..."            // for done — what was accomplished
}
Never wrap in markdown fences. Prefer small, correct steps over giant dumps.
Respect zero-lock-in: no Supabase/Firebase. Use vanilla Postgres patterns if needed.
"""


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


async def run_agent_loop(
    *,
    project_path: Path,
    user_goal: str,
    client,  # AsyncAnthropic
    model: str,
    max_steps: int = 6,
    write_fn: Optional[Callable[..., Awaitable[str]]] = None,
    verify_fn: Optional[Callable[..., Awaitable[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """
    write_fn(path, content) -> final content (may self-heal)
    verify_fn() -> verification report
    """
    transcript: List[Dict[str, Any]] = []
    written: List[str] = []
    messages = [
        {
            "role": "user",
            "content": f"Goal: {user_goal}\n\nStart by listing files or reading the main entry points, then implement the goal.",
        }
    ]

    for step in range(1, max_steps + 1):
        response = await client.messages.create(
            model=model,
            max_tokens=4096,
            system=AGENT_SYSTEM,
            messages=messages,
        )
        raw = response.content[0].text
        action = _extract_json(raw) or {
            "thought": "parse_failed",
            "action": "done",
            "summary": raw[:300],
        }
        transcript.append({"step": step, "raw": raw[:500], "action": action})

        act = (action.get("action") or "done").lower()
        path = action.get("path") or ""
        content = action.get("content") or ""

        observation = ""

        if act == "list_files":
            files = []
            for p in project_path.rglob("*"):
                if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts:
                    files.append(str(p.relative_to(project_path)))
            observation = "Files:\n" + "\n".join(sorted(files)[:80])

        elif act == "read_file":
            target = (project_path / path).resolve()
            if not str(target).startswith(str(project_path.resolve())):
                observation = "error: path outside workspace"
            elif not target.exists():
                observation = f"error: not found {path}"
            else:
                observation = target.read_text(encoding="utf-8")[:6000]

        elif act == "write_file":
            if not path or not content:
                observation = "error: path and content required"
            else:
                if write_fn:
                    class _Req:
                        project_id = project_path.name
                        user_prompt = user_goal
                        target_file = path

                    final = await write_fn(path, content, _Req())
                else:
                    full = project_path / path
                    full.parent.mkdir(parents=True, exist_ok=True)
                    full.write_text(content, encoding="utf-8")
                    final = content
                written.append(path)
                observation = f"wrote {path} ({len(final)} chars)"

        elif act == "verify":
            if verify_fn:
                report = await verify_fn()
                observation = json.dumps(report)[:2000]
            else:
                observation = "verify skipped (no verifier)"

        elif act == "done":
            return {
                "status": "success",
                "steps": step,
                "written_files": written,
                "summary": action.get("summary") or "done",
                "transcript": transcript,
            }

        else:
            observation = f"unknown action: {act}"

        messages.append({"role": "assistant", "content": raw})
        messages.append(
            {
                "role": "user",
                "content": f"Observation:\n{observation}\n\nContinue toward the goal. Use action=done when finished.",
            }
        )

    return {
        "status": "max_steps",
        "steps": max_steps,
        "written_files": written,
        "summary": "Stopped at max steps",
        "transcript": transcript,
    }
