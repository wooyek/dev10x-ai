from __future__ import annotations

import subprocess
from unittest.mock import AsyncMock, patch

import pytest

audit_mod = pytest.importorskip("dev10x.mcp.audit", reason="dev10x not installed")


class TestExtractSession:
    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_returns_output_on_success(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Extracted 42 turns",
            stderr="",
        )
        result = await audit_mod.extract_session(jsonl_path="/tmp/session.jsonl")
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_returns_error_on_failure(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="File not found",
        )
        result = await audit_mod.extract_session(jsonl_path="/tmp/missing.jsonl")
        assert "error" in result

    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_passes_output_path(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK",
            stderr="",
        )
        await audit_mod.extract_session(
            jsonl_path="/tmp/session.jsonl",
            output_path="/tmp/output.md",
        )
        call_args = mock_run.call_args
        assert "/tmp/output.md" in call_args.args[1:]


class TestAnalyzeActions:
    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_returns_output_on_success(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Analyzed 15 actions",
            stderr="",
        )
        result = await audit_mod.analyze_actions(transcript_path="/tmp/transcript.md")
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_returns_error_on_failure(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Parse error",
        )
        result = await audit_mod.analyze_actions(transcript_path="/tmp/transcript.md")
        assert "error" in result


class TestAnalyzePermissions:
    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_returns_output_on_success(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Found 3 friction points",
            stderr="",
        )
        result = await audit_mod.analyze_permissions(transcript_path="/tmp/transcript.md")
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_returns_error_on_failure(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Settings not found",
        )
        result = await audit_mod.analyze_permissions(transcript_path="/tmp/transcript.md")
        assert "error" in result

    @pytest.mark.asyncio
    @patch("dev10x.mcp.audit.async_run_script", new_callable=AsyncMock)
    async def test_passes_optional_paths(
        self,
        mock_run: AsyncMock,
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK",
            stderr="",
        )
        await audit_mod.analyze_permissions(
            transcript_path="/tmp/transcript.md",
            settings_path="/tmp/settings.json",
            output_path="/tmp/output.md",
        )
        call_args = mock_run.call_args
        assert "/tmp/settings.json" in call_args.args[1:]
        assert "/tmp/output.md" in call_args.args[1:]
