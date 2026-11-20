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


def test_export_max_obs_snv(real_db_name: str):
    """Test that --max-obs is accepted for SNV export."""

    runner = CliRunner()

    command = ["--database", real_db_name, "export", "--max-obs", "5"]

    result = runner.invoke(base_command, command)
    assert result.exit_code == 0


def test_export_max_obs_sv(real_db_name: str):
    """Test that --max-obs is accepted for SV export."""

    runner = CliRunner()

    command = ["--database", real_db_name, "export", "-t", "sv", "--max-obs", "5"]

    result = runner.invoke(base_command, command)
    assert result.exit_code == 0


def test_export_max_obs_must_be_positive(real_db_name: str):
    """Test that --max-obs must be a positive integer."""

    runner = CliRunner()

    command = ["--database", real_db_name, "export", "--max-obs", "0"]

    result = runner.invoke(base_command, command)
    assert result.exit_code == 2


def test_export_include_case_ids(real_mongo_adapter, real_db_name, vcf_path, ped_path, tmp_path):
    """Test that case ids are exported when --include-case-ids is used"""
    from loqusdb.constants import GRCH37
    from loqusdb.utils.load import load_database

    ## GIVEN a database with a loaded case
    load_database(
        adapter=real_mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH37,
    )
    outfile = tmp_path / "cases.vcf"

    runner = CliRunner()

    ## WHEN exporting with case ids
    command = [
        "--database",
        real_db_name,
        "export",
        "--include-case-ids",
        "-o",
        str(outfile),
    ]
    result = runner.invoke(base_command, command)

    ## THEN the header declares Cases and variant records list the case
    assert result.exit_code == 0
    content = outfile.read_text()
    assert "##INFO=<ID=Cases" in content
    assert "Cases=recessive_trio" in content


def test_export_default_has_no_case_ids(
    real_mongo_adapter, real_db_name, vcf_path, ped_path, tmp_path
):
    """Test that case ids are not exported by default"""
    from loqusdb.constants import GRCH37
    from loqusdb.utils.load import load_database

    ## GIVEN a database with a loaded case
    load_database(
        adapter=real_mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH37,
    )
    outfile = tmp_path / "no_cases.vcf"

    runner = CliRunner()

    ## WHEN exporting without the flag
    command = ["--database", real_db_name, "export", "-o", str(outfile)]
    result = runner.invoke(base_command, command)

    ## THEN no case ids appear in the output
    assert result.exit_code == 0
    content = outfile.read_text()
    assert "##INFO=<ID=Cases" not in content
    assert ";Cases=" not in content
