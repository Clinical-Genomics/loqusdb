from click.testing import CliRunner

from loqusdb.commands.cli import cli as base_command


def test_identity(real_db_name: str):
    """Test the SV identity base command."""

    runner = CliRunner()

    # WHEN the base identity command is run on an empty database
    command = ["--database", real_db_name, "identity", "-v", "1_7890024_TGA_GGG"]

    # THEN the command should return success
    result = runner.invoke(base_command, command)
    assert result.exit_code == 0

    # AND no variant found message
    assert "No hits for variant" in result.output
