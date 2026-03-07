"""Shared utilities for calling external scripts via subprocess."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any


def get_plugin_root() -> Path:
    """Get the plugin root directory."""
    return Path(__file__).parent.parent.parent


def run_script(
    script_path: str,
    *args: str,
    env_vars: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """
    Run an external script and return the result.

    Args:
        script_path: Relative path from plugin root (e.g., 'skills/gh/scripts/detect-tracker.sh')
        *args: Arguments to pass to the script
        env_vars: Additional environment variables

    Returns:
        CompletedProcess with stdout and stderr
    """
    plugin_root = get_plugin_root()
    full_path = plugin_root / script_path

    if not full_path.exists():
        raise FileNotFoundError(f"Script not found: {full_path}")

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    result = subprocess.run(
        [str(full_path), *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    return result


def parse_key_value_output(text: str) -> dict[str, str]:
    """
    Parse shell script output in key=value format.

    Args:
        text: Output from shell script (newline-separated key=value pairs)

    Returns:
        Dictionary of parsed key-value pairs
    """
    result = {}
    for line in text.strip().split("\n"):
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def parse_json_output(text: str) -> dict[str, Any]:
    """
    Parse JSON output from a script.

    Args:
        text: JSON string from script

    Returns:
        Parsed JSON as dictionary
    """
    return json.loads(text)
