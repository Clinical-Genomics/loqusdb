from loqusdb.commands import base_command

from click.testing import CliRunner

def test_base_command():
    runner = CliRunner()
    result = runner.invoke(base_command, [])
    
    assert result.exit_code == 0

class TestLoadCommand:
    
    # def test_load_command(self, mongo_client, vcf_path, ped_path):
    #     runner = CliRunner()
    #     command = ['-c', 'mongomock://', '--database', 'test', 'load', vcf_path, '-f', ped_path]
    #     result = runner.invoke(base_command, command)
    #
    #     assert result.exit_code == 0

    def test_load_command_no_ped(self, mongo_client, vcf_path):
        runner = CliRunner()
        command = ['-c', 'mongomock://', '--database', 'test', 'load', vcf_path]
        result = runner.invoke(base_command, command)
        
        assert result.exit_code == 1
    
# def test_delete_command(mongo_client, vcf_path, ped_path):
#     runner = CliRunner()
#
#     load_command = ['-c', 'mongomock://', '--database', 'test', 'load', vcf_path, '-f', ped_path]
#     runner.invoke(base_command, load_command)
#
#     delete_command = ['-c', 'mongomock://', '--database', 'test', 'delete', vcf_path, '-f', ped_path]
#     result = runner.invoke(base_command, delete_command)
#
#     assert result.exit_code == 0
#
#
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

