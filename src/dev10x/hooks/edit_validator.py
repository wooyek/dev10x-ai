"""Edit/Write tool validator — blocks sensitive file writes.

Loads rules from command-skill-map.yaml where matcher="Edit|Write",
iterates registered rules, first block wins.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_YAML_PATH = Path(__file__).parent.parent / "validators" / "command-skill-map.yaml"


@dataclass(frozen=True)
class EditRule:
    name: str
    file_pattern: re.Pattern[str] | None
    file_names: frozenset[str]
    file_prefixes: tuple[str, ...]
    file_substrings: tuple[str, ...]
    content_pattern: re.Pattern[str] | None
    message: str
    compensations: list[dict[str, str]] = field(default_factory=list)


def load_rules(*, yaml_path: Path = _YAML_PATH) -> list[EditRule]:
    data: dict[str, Any] = yaml.safe_load(yaml_path.read_text())
    rules: list[EditRule] = []
    for entry in data.get("rules", []):
        if entry.get("matcher") != "Edit|Write":
            continue
        if not entry.get("hook_block", False):
            continue
        fp = entry.get("file_pattern")
        cp = entry.get("content_pattern")
        rules.append(
            EditRule(
                name=entry.get("name", ""),
                file_pattern=re.compile(fp) if fp else None,
                file_names=frozenset(entry.get("file_names", [])),
                file_prefixes=tuple(entry.get("file_prefixes", [])),
                file_substrings=tuple(entry.get("file_substrings", [])),
                content_pattern=re.compile(cp) if cp else None,
                message=(entry.get("message") or entry.get("reason") or "BLOCKED").strip(),
                compensations=entry.get("compensations", []),
            )
        )
    return rules


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1] if "/" in path else path


def matches_file(*, rule: EditRule, file_path: str) -> bool:
    if rule.file_pattern and rule.file_pattern.search(file_path):
        return True
    name = _basename(path=file_path)
    if name in rule.file_names:
        return True
    if any(name.startswith(p) for p in rule.file_prefixes):
        return True
    return any(s in file_path for s in rule.file_substrings)


def matches_content(*, rule: EditRule, content: str) -> bool:
    if rule.content_pattern is None:
        return True
    return rule.content_pattern.search(content) is not None


def format_message(*, rule: EditRule, file_path: str) -> str:
    msg = rule.message.format(file_path=file_path)
    for comp in rule.compensations:
        desc = comp.get("description", "")
        if desc:
            msg += f"\n\n{desc.strip()}"
    return msg


def block(*, message: str) -> None:
    result = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": message,
    }
    print(json.dumps(result), file=sys.stderr)
    sys.exit(2)


def validate_edit_write(
    *,
    data: dict[str, Any],
    yaml_path: Path | None = None,
    debug: bool = False,
) -> None:
    tool = data.get("tool_name", "")
    if tool not in ("Edit", "Write"):
        sys.exit(0)

    inp = data.get("tool_input", {})
    file_path = inp.get("file_path", "")
    content = inp.get("new_string") or inp.get("content", "")

    resolved_path = yaml_path or _YAML_PATH
    rules = load_rules(yaml_path=resolved_path)

    if debug:
        print(f"[DEBUG] Loaded {len(rules)} Edit|Write rules", file=sys.stderr)

    for rule in rules:
        if not matches_file(rule=rule, file_path=file_path):
            continue
        if not matches_content(rule=rule, content=content):
            continue
        if debug:
            print(f"[DEBUG] Rule '{rule.name}' matched: {file_path}", file=sys.stderr)
        block(message=format_message(rule=rule, file_path=file_path))

    sys.exit(0)
