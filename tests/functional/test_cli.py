from loqusdb.commands import base_command

from click.testing import CliRunner

def test_base_command():
    runner = CliRunner()
    result = runner.invoke(base_command, [])
    
    assert result.exit_code == 0

class TestLoadCommand:
    
    def test_load_command(self, real_mongo_client, vcf_path, ped_path):
        runner = CliRunner()
        result = runner.invoke(base_command, ['--database', 'test', 'load', vcf_path, '-f', ped_path])
        
        assert result.exit_code == 0

    def test_load_command_no_ped(self, real_mongo_client, vcf_path):
        runner = CliRunner()
        result = runner.invoke(base_command, ['--database', 'test', 'load', vcf_path])
        
        assert result.exit_code == 1
    
def test_delete_command(real_mongo_client, vcf_path, ped_path):
    runner = CliRunner()
    runner.invoke(base_command, ['--database', 'test', 'load', vcf_path, '-f', ped_path])
    
    result = runner.invoke(base_command, ['--database', 'test', 'delete', vcf_path, '-f', ped_path])
    
    assert result.exit_code == 0


def test_wipe_command(real_mongo_client, vcf_path, ped_path):
    runner = CliRunner()
    runner.invoke(base_command, ['--database', 'test', 'load', vcf_path, '-f', ped_path])
    
    result = runner.invoke(base_command, ['--database', 'test', 'wipe', '--yes'])
    
    assert result.exit_code == 0

