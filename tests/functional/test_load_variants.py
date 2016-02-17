from loqusdb.commands import base_command

from click.testing import CliRunner

class TestBaseCommand:
    
    runner = CliRunner()
    result = runner.invoke(cli, [])
    
    assert result.exit_code = 0

