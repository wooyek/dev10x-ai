from __future__ import annotations

import subprocess
from unittest.mock import AsyncMock, patch

import pytest

perm_mod = pytest.importorskip("dev10x.mcp.permission", reason="dev10x not installed")


class TestUpdatePaths:
    @pytest.mark.asyncio
    @patch("dev10x.mcp.permission.async_run", new_callable=AsyncMock)
    async def test_returns_output_on_success(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Updated 3 files",
            stderr="",
        )
        result = await perm_mod.update_paths()
        assert result["success"] is True
        assert "Updated 3 files" in result["output"]

    @pytest.mark.asyncio
    @patch("dev10x.mcp.permission.async_run", new_callable=AsyncMock)
    async def test_returns_error_on_failure(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Config not found",
        )
        result = await perm_mod.update_paths()
        assert "error" in result

    @pytest.mark.asyncio
    @patch("dev10x.mcp.permission.async_run", new_callable=AsyncMock)
    async def test_passes_flags(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK",
            stderr="",
        )
        await perm_mod.update_paths(
            version="1.0.0",
            dry_run=True,
            ensure_base=True,
            generalize=True,
            init=True,
            quiet=True,
        )
        call_args = mock_run.call_args
        args_list = call_args.kwargs["args"]
        assert "--version" in args_list
        assert "1.0.0" in args_list
        assert "--dry-run" in args_list
        assert "--ensure-base" in args_list
        assert "--generalize" in args_list
        assert "--init" in args_list
        assert "--quiet" in args_list
