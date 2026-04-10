"""Permission maintenance MCP tool implementations.

Wraps update-paths.py as an MCP tool so skills can update
plugin permission settings without Bash allow-rule friction.
"""

from __future__ import annotations

from typing import Any

from dev10x.mcp.subprocess_utils import async_run, get_plugin_root


async def update_paths(
    *,
    version: str | None = None,
    dry_run: bool = False,
    ensure_base: bool = False,
    generalize: bool = False,
    init: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    script = get_plugin_root() / "skills/upgrade-cleanup/scripts/update-paths.py"
    args: list[str] = [str(script)]

    if version:
        args.extend(["--version", version])
    if dry_run:
        args.append("--dry-run")
    if ensure_base:
        args.append("--ensure-base")
    if generalize:
        args.append("--generalize")
    if init:
        args.append("--init")
    if quiet:
        args.append("--quiet")

    result = await async_run(args=args, timeout=60)

    if result.returncode != 0:
        return {"error": result.stderr.strip()}

    return {"success": True, "output": result.stdout.strip()}
