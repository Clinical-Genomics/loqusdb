from click.testing import CliRunner

from loqusdb.commands.cli import cli as base_command


def test_export_base(real_db_name: str):
    """Test the base command that exports variants."""

    runner = CliRunner()

    # WHEN the base command to export cases is run
    command = ["--database", real_db_name, "export"]

    ## THEN it should return success
    result = runner.invoke(base_command, command)
    assert result.exit_code == 0
