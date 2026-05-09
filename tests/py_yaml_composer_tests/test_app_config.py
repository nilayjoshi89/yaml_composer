"""Tests for app_config.py AppConfig class."""
from unittest.mock import patch

import pytest

from py_yaml_composer.utility.app_config import AppConfig


class TestAppConfig:
    """Test AppConfig class initialization and parsing."""

    def test_parse_arg_default_values(self) -> None:
        """Test parse_arg with minimal arguments."""
        # arrange
        test_args = ["prog", "test.yaml"]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert
        assert AppConfig.Filename == "test.yaml"
        assert AppConfig.Workspace == "/yaml_workspace"

    def test_parse_arg_with_workspace_option_short_flag(self) -> None:
        """Test parse_arg with -w workspace flag."""
        # arrange
        test_args = ["prog", "test.yaml", "-w", "/custom/workspace"]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert
        assert AppConfig.Filename == "test.yaml"
        assert AppConfig.Workspace == "/custom/workspace"

    def test_parse_arg_with_workspace_option_long_flag(self) -> None:
        """Test parse_arg with --workspace flag."""
        # arrange
        test_args = ["prog", "template.yaml", "--workspace", "C:\\yaml\\templates"]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert
        assert AppConfig.Filename == "template.yaml"
        assert AppConfig.Workspace == "C:\\yaml\\templates"

    def test_parse_arg_with_relative_path_filename(self) -> None:
        """Test parse_arg with relative path filename."""
        # arrange
        test_args = ["prog", "subfolder/config.yaml"]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert
        assert AppConfig.Filename == "subfolder/config.yaml"

    def test_parse_arg_with_absolute_path_filename(self) -> None:
        """Test parse_arg with absolute path filename."""
        # arrange
        test_args = ["prog", "/absolute/path/to/template.yaml"]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert
        assert AppConfig.Filename == "/absolute/path/to/template.yaml"

    def test_parse_arg_missing_filename_raises_error(self) -> None:
        """Test parse_arg raises error when filename is not provided."""
        # arrange
        test_args = ["prog"]

        # act & assert
        with patch("sys.argv", test_args), pytest.raises(SystemExit):
            AppConfig.parse_arg()

    def test_parse_arg_empty_workspace_keeps_empty(self) -> None:
        """Test parse_arg when workspace is explicitly set to empty string."""
        # arrange
        test_args = ["prog", "test.yaml", "-w", ""]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert - empty string is kept as-is (args.workspace check is against empty string)
        assert AppConfig.Filename == "test.yaml"
        assert AppConfig.Workspace == ""

    def test_parse_arg_workspace_with_spaces(self) -> None:
        """Test parse_arg with workspace path containing spaces."""
        # arrange
        test_args = ["prog", "test.yaml", "-w", "/path with spaces/workspace"]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert
        assert AppConfig.Workspace == "/path with spaces/workspace"

    def test_parse_arg_preserves_filename_casing(self) -> None:
        """Test parse_arg preserves filename case."""
        # arrange
        test_args = ["prog", "MyTemplate.YAML"]

        # act
        with patch("sys.argv", test_args):
            AppConfig.parse_arg()

        # assert
        assert AppConfig.Filename == "MyTemplate.YAML"

    def test_parse_arg_multiple_calls_updates_values(self) -> None:
        """Test that multiple parse_arg calls update the static values."""
        # arrange
        test_args_1 = ["prog", "first.yaml", "-w", "/first"]
        test_args_2 = ["prog", "second.yaml", "-w", "/second"]

        # act
        with patch("sys.argv", test_args_1):
            AppConfig.parse_arg()
        first_filename = AppConfig.Filename
        first_workspace = AppConfig.Workspace

        with patch("sys.argv", test_args_2):
            AppConfig.parse_arg()
        second_filename = AppConfig.Filename
        second_workspace = AppConfig.Workspace

        # assert
        assert first_filename == "first.yaml"
        assert first_workspace == "/first"
        assert second_filename == "second.yaml"
        assert second_workspace == "/second"
