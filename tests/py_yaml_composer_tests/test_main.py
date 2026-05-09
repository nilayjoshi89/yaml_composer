"""Tests for main.py entry_point function."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from py_yaml_composer.main import entry_point


class TestMainEntryPoint:
    """Test main.py entry_point function."""

    def test_entry_point_with_valid_template(self, capsys: Any) -> None:
        """Test entry_point processes a valid template file."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid template
            template_path = Path(tmpdir) / "template.yaml"
            template_path.write_text("X-OUTPUT: output.yaml\nNode1: Value1\n")

            test_args = ["prog", "template.yaml", "-w", tmpdir]

            # act
            with patch("sys.argv", test_args), patch("sys.exit"):
                entry_point()

            # assert
            captured = capsys.readouterr()
            assert "output.yaml" in captured.out

    def test_entry_point_calls_parse_arg(self) -> None:
        """Test that entry_point calls AppConfig.parse_arg."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "test.yaml"
            template_path.write_text("X-OUTPUT: out.yaml\nkey: value\n")

            test_args = ["prog", "test.yaml", "-w", tmpdir]

            # act
            with (
                patch("sys.argv", test_args),
                patch("py_yaml_composer.main.AppConfig.parse_arg"),
                patch("sys.exit"),
                patch("py_yaml_composer.main.YamlGenerator") as mock_gen,
            ):
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.start.return_value = "output.yaml"

                entry_point()

    def test_entry_point_creates_yaml_generator_with_correct_components(
        self,
    ) -> None:
        """Test that entry_point creates YamlGenerator with correct components."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "test.yaml"
            template_path.write_text("X-OUTPUT: out.yaml\nkey: value\n")

            test_args = ["prog", "test.yaml", "-w", tmpdir]

            # act
            with (
                patch("sys.argv", test_args),
                patch("py_yaml_composer.main.YamlGenerator") as mock_gen,
            ):
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.start.return_value = "output.yaml"

                with patch("sys.exit"):
                    entry_point()

                # assert
                mock_gen.assert_called_once()
                call_kwargs = mock_gen.call_args[1]
                assert "file_helper" in call_kwargs
                assert "traverser" in call_kwargs
                assert "multistage_actions" in call_kwargs

    def test_entry_point_calls_generator_start_with_filename(self) -> None:
        """Test that entry_point calls generator.start() with filename."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.yaml"
            template_path.write_text("X-OUTPUT: out.yaml\n")

            test_args = ["prog", "template.yaml", "-w", tmpdir]

            # act
            with (
                patch("sys.argv", test_args),
                patch("py_yaml_composer.main.YamlGenerator") as mock_gen,
            ):
                mock_instance = MagicMock()
                mock_gen.return_value = mock_instance
                mock_instance.start.return_value = "output.yaml"

                with patch("sys.exit"):
                    entry_point()

                # assert
                mock_instance.start.assert_called_once_with(
                    file_path="template.yaml"
                )

    def test_entry_point_prints_output_path(self, capsys: Any) -> None:
        """Test that entry_point prints the output file path."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "test.yaml"
            template_path.write_text("X-OUTPUT: result.yaml\ntest: data\n")

            test_args = ["prog", "test.yaml", "-w", tmpdir]

            # act
            with patch("sys.argv", test_args), patch("sys.exit"):
                entry_point()

            # assert
            captured = capsys.readouterr()
            assert "result.yaml" in captured.out

    def test_entry_point_exits_with_zero(self) -> None:
        """Test that entry_point calls sys.exit(0)."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "test.yaml"
            template_path.write_text("X-OUTPUT: out.yaml\nkey: val\n")

            test_args = ["prog", "test.yaml", "-w", tmpdir]

            # act
            with patch("sys.argv", test_args), patch("sys.exit") as mock_exit:
                entry_point()

                # assert
                mock_exit.assert_called_once_with(0)

    def test_entry_point_with_subdirectory_template(self) -> None:
        """Test entry_point with template in subdirectory."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "templates"
            subdir.mkdir()
            template_path = subdir / "test.yaml"
            template_path.write_text("X-OUTPUT: output.yaml\ndata: value\n")

            test_args = ["prog", "templates/test.yaml", "-w", tmpdir]

            # act
            with patch("sys.argv", test_args), patch("sys.exit"):
                entry_point()

            # assert - should not raise an error

    def test_entry_point_file_helper_is_yaml_file_helper(self) -> None:
        """Test that entry_point uses YamlFileHelper."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "test.yaml"
            template_path.write_text("X-OUTPUT: out.yaml\n")

            test_args = ["prog", "test.yaml", "-w", tmpdir]

            # act
            with (
                patch("sys.argv", test_args),
                patch("py_yaml_composer.main.YamlFileHelper") as mock_helper,
            ):
                mock_instance = MagicMock()
                mock_helper.return_value = mock_instance

                with (
                    patch("py_yaml_composer.main.YamlGenerator"),
                    patch("sys.exit"),
                ):
                    entry_point()

                # assert
                mock_helper.assert_called_once()

    def test_entry_point_traverser_is_yaml_traverser(self) -> None:
        """Test that entry_point uses YamlTraverser."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "test.yaml"
            template_path.write_text("X-OUTPUT: out.yaml\n")

            test_args = ["prog", "test.yaml", "-w", tmpdir]

            # act
            with (
                patch("sys.argv", test_args),
                patch("py_yaml_composer.main.YamlTraverser") as mock_traverser,
            ):
                mock_instance = MagicMock()
                mock_traverser.return_value = mock_instance

                with (
                    patch("py_yaml_composer.main.YamlGenerator"),
                    patch("sys.exit"),
                ):
                    entry_point()

                # assert
                mock_traverser.assert_called_once()

    def test_entry_point_actions_are_default_actions(self) -> None:
        """Test that entry_point uses DefaultActions."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "test.yaml"
            template_path.write_text("X-OUTPUT: out.yaml\n")

            test_args = ["prog", "test.yaml", "-w", tmpdir]

            # act
            with (
                patch("sys.argv", test_args),
                patch("py_yaml_composer.main.DefaultActions") as mock_actions,
            ):
                mock_actions.get.return_value = []

                with (
                    patch("py_yaml_composer.main.YamlGenerator"),
                    patch("sys.exit"),
                ):
                    entry_point()

                # assert
                mock_actions.get.assert_called_once()

    def test_entry_point_with_complex_template(self, capsys: Any) -> None:
        """Test entry_point with template containing references."""
        # arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            ref_path = Path(tmpdir) / "refs.yaml"
            ref_path.write_text(
                "X-REF-Database:\n  host: db.example.com\n  port: 5432\n"
            )

            template_path = Path(tmpdir) / "template.yaml"
            template_path.write_text(
                "X-OUTPUT: config.yaml\n"
                "X-INCLUDE:\n"
                "  - refs.yaml\n"
                "app:\n"
                "  name: MyApp\n"
                "  database: X-REF-Database\n"
            )

            test_args = ["prog", "template.yaml", "-w", tmpdir]

            # act
            with patch("sys.argv", test_args), patch("sys.exit"):
                entry_point()

            # assert
            captured = capsys.readouterr()
            assert "config.yaml" in captured.out
            # Check that config.yaml was created
            config_file = Path(tmpdir) / "config.yaml"
            assert config_file.exists()
