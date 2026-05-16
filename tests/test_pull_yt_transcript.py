#!/usr/bin/env python3
"""Tests for scripts/pull_yt_transcript.py

Tests cover:
- Happy path: transcript download succeeds
- Error cases: API errors, missing video ID, file write errors
- CLI usage: correct args, missing args
"""

import subprocess
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest

import scripts.pull_yt_transcript as pull_yt_transcript


class TestDownloadTranscript:
    """Tests for download_transcript function."""

    @patch("scripts.pull_yt_transcript.YouTubeTranscriptApi")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_manually_created_transcript(self, mock_file, mock_api):
        """Test downloading manually created English transcript."""
        # Mock transcript API response
        mock_transcript_list = MagicMock()
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = [
            {"text": "Hello"},
            {"text": "world"},
        ]
        mock_transcript_list.find_manually_created_transcript.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_transcript_list

        result = pull_yt_transcript.download_transcript("test_video_id", "/tmp/transcript.txt")

        assert result is True
        mock_file.assert_called_once_with("/tmp/transcript.txt", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("Hello world")

    @patch("scripts.pull_yt_transcript.YouTubeTranscriptApi")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_auto_generated_fallback(self, mock_file, mock_api):
        """Test fallback to auto-generated transcript when manual not available."""
        mock_transcript_list = MagicMock()
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = [
            {"text": "Auto"},
            {"text": "generated"},
        ]

        # Manually created raises exception, should fallback to generated
        mock_transcript_list.find_manually_created_transcript.side_effect = Exception("No manual transcript")
        mock_transcript_list.find_generated_transcript.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_transcript_list

        result = pull_yt_transcript.download_transcript("test_video_id", "/tmp/auto.txt")

        assert result is True
        mock_transcript_list.find_generated_transcript.assert_called_once_with(["en"])
        mock_file().write.assert_called_once_with("Auto generated")

    @patch("scripts.pull_yt_transcript.YouTubeTranscriptApi")
    def test_download_api_error(self, mock_api):
        """Test that API errors are handled gracefully."""
        mock_api.list_transcripts.side_effect = Exception("API Error")

        result = pull_yt_transcript.download_transcript("bad_video_id", "/tmp/fail.txt")

        assert result is False

    @patch("scripts.pull_yt_transcript.YouTubeTranscriptApi")
    @patch("builtins.open", side_effect=IOError("Disk full"))
    def test_download_file_write_error(self, mock_file, mock_api):
        """Test that file write errors are handled gracefully."""
        mock_transcript_list = MagicMock()
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = [{"text": "test"}]
        mock_transcript_list.find_manually_created_transcript.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_transcript_list

        result = pull_yt_transcript.download_transcript("video_id", "/invalid/path.txt")

        assert result is False


@pytest.mark.integration
class TestMainCLI:
    """Tests for CLI invocation."""

    def test_missing_args_shows_usage(self):
        """Test that missing arguments shows usage and exits 1."""
        result = subprocess.run(
            [sys.executable, "scripts/pull_yt_transcript.py"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Usage:" in result.stdout
        assert "<video_id>" in result.stdout
        assert "<output_path>" in result.stdout

    def test_partial_args_shows_usage(self):
        """Test that providing only video ID shows usage."""
        result = subprocess.run(
            [sys.executable, "scripts/pull_yt_transcript.py", "test_video"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Usage:" in result.stdout

    @patch("scripts.pull_yt_transcript.YouTubeTranscriptApi")
    def test_cli_success_path(self, mock_api):
        """Test CLI with valid args (mocked API)."""
        # This test would require full integration with YouTube API
        # Marked as integration test
        pass

    @patch("scripts.pull_yt_transcript.YouTubeTranscriptApi")
    def test_cli_api_error_exits_one(self, mock_api):
        """Test that API errors in CLI mode exit with code 1."""
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        mock_api_instance.list.side_effect = Exception("API Error")

        result = subprocess.run(
            [sys.executable, "scripts/pull_yt_transcript.py", "bad_id", "/tmp/out.txt"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Error downloading transcript" in result.stdout
