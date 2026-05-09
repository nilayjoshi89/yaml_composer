"""Tests for yaml_helper.py YamlFileHelper class."""

import tempfile
from pathlib import Path
from typing import Any

import pytest

from py_yaml_composer.utility.app_config import AppConfig
from py_yaml_composer.utility.files.yaml_helper import YamlFileHelper


class TestYamlFileHelper:
    """Test YamlFileHelper file operations."""

    def setup_method(self) -> None:
        """Reset AppConfig before each test."""
        AppConfig.Workspace = ""
        AppConfig.Filename = ""

    def test_load_yaml_file_relative_path(self) -> None:
        """Test loading YAML file with relative path."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            test_file = Path(tmpdir) / "test.yaml"
            test_file.write_text("key: value\nnumber: 42\n")

            helper = YamlFileHelper()

            # act
            result = helper.load("test.yaml")

            # assert
            assert result["key"] == "value"
            assert result["number"] == 42

    def test_load_yaml_file_absolute_path(self) -> None:
        """Test loading YAML file with absolute path."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "absolute_test.yaml"
            test_file.write_text("name: test\nactive: true\n")

            helper = YamlFileHelper()

            # act
            result = helper.load(str(test_file))

            # assert
            assert result["name"] == "test"
            assert result["active"] is True

    def test_load_yaml_with_nested_structure(self) -> None:
        """Test loading YAML with nested dictionaries and lists."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            test_file = Path(tmpdir) / "nested.yaml"
            test_file.write_text(
                "app:\n  name: MyApp\n  services:\n    - db\n    - cache\n"
            )

            helper = YamlFileHelper()

            # act
            result = helper.load("nested.yaml")

            # assert
            assert result["app"]["name"] == "MyApp"
            assert result["app"]["services"] == ["db", "cache"]

    def test_save_yaml_file_relative_path(self) -> None:
        """Test saving YAML file with relative path."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            data: dict[Any, Any] = {
                "key": "value",
                "number": 42,
            }

            helper = YamlFileHelper()

            # act
            helper.save(data, "output.yaml")

            # assert
            output_file = Path(tmpdir) / "output.yaml"
            assert output_file.exists()
            loaded = output_file.read_text()
            assert "key: value" in loaded
            assert "number: 42" in loaded

    def test_save_yaml_file_absolute_path(self) -> None:
        """Test saving YAML file with absolute path."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "absolute_output.yaml"
            data: dict[Any, Any] = {
                "saved": True,
            }

            helper = YamlFileHelper()

            # act
            helper.save(data, str(output_path))

            # assert
            assert output_path.exists()
            content = output_path.read_text()
            assert "saved: true" in content

    def test_save_yaml_with_nested_structure(self) -> None:
        """Test saving YAML with nested dictionaries."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            data: dict[Any, Any] = {
                "app": {
                    "name": "TestApp",
                    "version": "1.0",
                    "services": ["web", "db"],
                }
            }

            helper = YamlFileHelper()

            # act
            helper.save(data, "config.yaml")

            # assert
            loaded_data = helper.load("config.yaml")
            assert loaded_data["app"]["name"] == "TestApp"
            assert loaded_data["app"]["version"] == "1.0"
            assert loaded_data["app"]["services"] == ["web", "db"]

    def test_exists_returns_true_for_existing_file(self) -> None:
        """Test exists returns True for existing file."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            test_file = Path(tmpdir) / "exists.yaml"
            test_file.write_text("test: true\n")

            helper = YamlFileHelper()

            # act
            result = helper.exists("exists.yaml")

            # assert
            assert result is True

    def test_exists_returns_false_for_missing_file(self) -> None:
        """Test exists returns False for non-existent file."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            helper = YamlFileHelper()

            # act
            result = helper.exists("does_not_exist.yaml")

            # assert
            assert result is False

    def test_exists_with_absolute_path(self) -> None:
        """Test exists with absolute path."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yaml"
            test_file.write_text("data: value\n")

            helper = YamlFileHelper()

            # act
            exists = helper.exists(str(test_file))

            # assert
            assert exists is True

    def test_get_workspace_path_relative(self) -> None:
        """Test get_workspace_path with relative path."""
        # arrange
        AppConfig.Workspace = "/workspace"
        helper = YamlFileHelper()

        # act
        path = helper.get_workspace_path("config.yaml")

        # assert - Path.joinpath converts to OS-specific separators
        assert "config.yaml" in path
        assert path.endswith("config.yaml")

    def test_get_workspace_path_absolute(self) -> None:
        """Test get_workspace_path with absolute path."""
        # arrange
        AppConfig.Workspace = "/workspace"
        helper = YamlFileHelper()

        # act
        path = helper.get_workspace_path("/absolute/config.yaml")

        # assert - absolute paths are returned as-is (converted to Path first)
        assert path.endswith("config.yaml")
        assert "absolute" in path

    def test_get_workspace_path_with_subdirectory(self) -> None:
        """Test get_workspace_path with subdirectory."""
        # arrange
        AppConfig.Workspace = "/workspace"
        helper = YamlFileHelper()

        # act
        path = helper.get_workspace_path("templates/config.yaml")

        # assert
        assert "templates" in path
        assert "config.yaml" in path

    def test_load_empty_yaml_file_raises_error(self) -> None:
        """Test loading empty YAML file raises TypeError."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            test_file = Path(tmpdir) / "empty.yaml"
            test_file.write_text("")

            helper = YamlFileHelper()

            # act & assert - empty YAML returns None which can't be converted to dict
            with pytest.raises(TypeError):
                helper.load("empty.yaml")

    def test_load_yaml_with_special_characters(self) -> None:
        """Test loading YAML with special characters."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            test_file = Path(tmpdir) / "special.yaml"
            test_file.write_text(
                'name: "Test with: colon"\n'
                'path: "/path/to/file"\n'
                'message: "Quote \\"test\\""\n'
            )

            helper = YamlFileHelper()

            # act
            result = helper.load("special.yaml")

            # assert
            assert "colon" in result["name"]
            assert result["path"] == "/path/to/file"

    def test_save_yaml_preserves_structure(self) -> None:
        """Test that saved YAML preserves data structure on reload."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            original_data: dict[Any, Any] = {
                "string": "value",
                "number": 123,
                "float": 45.67,
                "boolean": True,
                "list": [1, 2, 3],
                "nested": {"key": "value"},
            }

            helper = YamlFileHelper()

            # act
            helper.save(original_data, "data.yaml")
            loaded_data = helper.load("data.yaml")

            # assert
            assert loaded_data["string"] == original_data["string"]
            assert loaded_data["number"] == original_data["number"]
            assert loaded_data["float"] == original_data["float"]
            assert loaded_data["boolean"] == original_data["boolean"]
            assert loaded_data["list"] == original_data["list"]
            assert loaded_data["nested"] == original_data["nested"]

    def test_load_nonexistent_file_raises_error(self) -> None:
        """Test that loading non-existent file raises error."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            AppConfig.Workspace = tmpdir
            helper = YamlFileHelper()

            # act & assert
            with pytest.raises(FileNotFoundError):
                helper.load("nonexistent.yaml")

    def test_workspace_with_windows_path(self) -> None:
        """Test get_workspace_path with Windows-style paths."""
        # arrange
        AppConfig.Workspace = "C:\\workspace"
        helper = YamlFileHelper()

        # act
        path = helper.get_workspace_path("config.yaml")

        # assert
        assert "config.yaml" in path

    def test_get_workspace_path_with_dots(self) -> None:
        """Test get_workspace_path with relative path using dots."""
        # arrange
        AppConfig.Workspace = "/workspace"
        helper = YamlFileHelper()

        # act
        path = helper.get_workspace_path("./config.yaml")

        # assert
        assert "config.yaml" in path
