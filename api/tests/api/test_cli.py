"""Test cli entrypoint."""

import pytest
from typer.testing import CliRunner

from api import cli


class TestCli:
    """Test cli."""

    runner = CliRunner()

    @pytest.mark.enable_loguru
    def test_cli_help(self) -> None:
        """Test cli help."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Show this message and exit." in result.output
        assert "CLI command to run the API application." in result.output
