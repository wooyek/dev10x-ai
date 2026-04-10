"""Skill audit MCP tool implementations.

Wraps the skill-audit 3-script pipeline as MCP tools so the
skill-audit skill can process sessions without Bash allow-rules.
"""

from __future__ import annotations

from typing import Any

from dev10x.mcp.subprocess_utils import async_run_script


async def extract_session(
    *,
    jsonl_path: str,
    output_path: str | None = None,
) -> dict[str, Any]:
    args = [jsonl_path]
    if output_path:
        args.append(output_path)

    result = await async_run_script(
        "skills/skill-audit/scripts/extract-session.py",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"success": True, "output": result.stdout.strip()}


async def analyze_actions(
    *,
    transcript_path: str,
    output_path: str | None = None,
) -> dict[str, Any]:
    args = [transcript_path]
    if output_path:
        args.append(output_path)

    result = await async_run_script(
        "skills/skill-audit/scripts/analyze-actions.py",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"success": True, "output": result.stdout.strip()}


async def analyze_permissions(
    *,
    transcript_path: str,
    settings_path: str | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    args = [transcript_path]
    if settings_path:
        args.append(settings_path)
    if output_path:
        args.append(output_path)

    result = await async_run_script(
        "skills/skill-audit/scripts/analyze-permissions.py",
        *args,
    )

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"success": True, "output": result.stdout.strip()}
