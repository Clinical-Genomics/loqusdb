from click.testing import CliRunner

from loqusdb.commands.cli import cli as base_command

def test_view_cases_no_cases(vcf_path, ped_path, real_mongo_adapter, real_db_name):
    """Test the command that returns database cases."""

    ## GIVEN an empty database
    assert sum([1 for _ in real_mongo_adapter.cases()]) == 0

    runner = CliRunner()

    # THEN the case command should return No cases found error
    command = ["--database", real_db_name, "cases" ]
    result = runner.invoke(base_command, command)
    assert result.exit_code == 1
    assert "No cases found in database" in result.output