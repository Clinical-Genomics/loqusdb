from pprint import pprint as pp

from loqusdb.commands import base_command

from click.testing import CliRunner

def test_base_command():
    runner = CliRunner()
    result = runner.invoke(base_command, [])

    assert result.exit_code == 0


def test_load_command(vcf_path, ped_path, real_mongo_adapter):
    ## GIVEN a vcf_path a ped_path
    runner = CliRunner()
    ## WHEN inserting a case via the CLI
    command = ['--database', 'test', 'load', '--variant-file', vcf_path, '-f', ped_path]
    result = runner.invoke(base_command, command)
    ## THEN assert that the cli exits without problems
    assert result.exit_code == 0

def test_load_command_no_ped(vcf_path):
    runner = CliRunner()
    command = ['--database', 'test', 'load', '--variant-file', vcf_path]
    result = runner.invoke(base_command, command)

    assert result.exit_code == 1

# def test_delete_command(mongo_client, vcf_path, ped_path):
#     runner = CliRunner()
#
#     load_command = ['--test', '--database', 'test', 'load', vcf_path, '-f', ped_path]
#     result = runner.invoke(base_command, load_command)
#
#     delete_command = ['--test', '--database', 'test', 'delete', vcf_path, '-f', ped_path]
#     result = runner.invoke(base_command, delete_command)
#
#     assert result.exit_code == 0


# def test_wipe_command(mongo_client, vcf_path, ped_path):
#     runner = CliRunner()
#
#     load_command = ['-c', 'mongomock://', '--database', 'test', 'load', vcf_path, '-f', ped_path]
#     runner.invoke(base_command, load_command)
#
#     wipe_command = ['-c', 'mongomock://', '--database', 'test', 'wipe', '--yes']
#     result = runner.invoke(base_command, wipe_command)
#
#     assert result.exit_code == 0
