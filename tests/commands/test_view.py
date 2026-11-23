import json
import re

from click.testing import CliRunner

from loqusdb.commands.cli import cli as base_command
from loqusdb.plugins.mongo.adapter import MongoAdapter


def test_view_cases_base(real_mongo_adapter: MongoAdapter, real_db_name: str):
    """Test the base command that returns database cases."""

    ## GIVEN an empty database
    assert sum([1 for _ in real_mongo_adapter.cases()]) == 0

    runner = CliRunner()

    # THEN the case command should return No cases found error
    command = ["--database", real_db_name, "cases"]
    result = runner.invoke(base_command, command)
    assert result.exit_code == 1
    assert "No cases found in database" in result.output


def _stdout(output):
    """Return the command output without the log lines that loqusdb writes"""
    return "\n".join(
        line for line in output.splitlines() if not re.match(r"^\d{4}-\d{2}-\d{2} ", line)
    )


def _load_case(real_mongo_adapter, vcf_path, ped_path):
    """Load a case with SNVs into the real test database"""
    from loqusdb.constants import GRCH37
    from loqusdb.utils.load import load_database

    load_database(
        adapter=real_mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        family_type="ped",
        genome_build=GRCH37,
    )


def test_view_cases_count(real_mongo_adapter, real_db_name, vcf_path, ped_path):
    """Test that the number of cases is printed"""
    ## GIVEN a database with one case
    _load_case(real_mongo_adapter, vcf_path, ped_path)

    runner = CliRunner()

    ## WHEN counting the cases
    result = runner.invoke(base_command, ["--database", real_db_name, "cases", "--count"])

    ## THEN the count is printed
    assert result.exit_code == 0
    assert _stdout(result.output).strip() == "1"


def test_view_cases_list(real_mongo_adapter, real_db_name, vcf_path, ped_path, case_id):
    """Test that all cases are listed with their VCF path"""
    ## GIVEN a database with one case
    _load_case(real_mongo_adapter, vcf_path, ped_path)

    runner = CliRunner()

    ## WHEN listing the cases
    result = runner.invoke(base_command, ["--database", real_db_name, "cases"])

    ## THEN the header and the case are printed
    assert result.exit_code == 0
    lines = _stdout(result.output).splitlines()
    assert lines[0] == "#case_id\tvcf_path"
    assert f"{case_id}\t{vcf_path}" in lines


def test_view_cases_by_case_id_json(real_mongo_adapter, real_db_name, vcf_path, ped_path, case_id):
    """Test that a single case can be printed as JSON"""
    ## GIVEN a database with one case
    _load_case(real_mongo_adapter, vcf_path, ped_path)

    runner = CliRunner()

    ## WHEN asking for the case as JSON
    command = ["--database", real_db_name, "cases", "-c", case_id, "--to-json"]
    result = runner.invoke(base_command, command)

    ## THEN the case is printed as a JSON list
    assert result.exit_code == 0
    cases = json.loads(_stdout(result.output))
    assert len(cases) == 1
    assert cases[0]["case_id"] == case_id


def test_view_cases_by_case_id_missing(real_mongo_adapter, real_db_name, vcf_path, ped_path):
    """Test that a missing case prints nothing"""
    ## GIVEN a database with one case
    _load_case(real_mongo_adapter, vcf_path, ped_path)

    runner = CliRunner()

    ## WHEN asking for a case that does not exist
    command = ["--database", real_db_name, "cases", "-c", "not_a_case"]
    result = runner.invoke(base_command, command)

    ## THEN nothing is printed and the command succeeds
    assert result.exit_code == 0
    assert _stdout(result.output).strip() == ""


def test_view_variant_by_id(real_mongo_adapter, real_db_name, vcf_path, ped_path):
    """Test that a single SNV can be looked up by its ID"""
    ## GIVEN a database with variants
    _load_case(real_mongo_adapter, vcf_path, ped_path)
    variant_id = real_mongo_adapter.db.variant.find_one()["_id"]

    runner = CliRunner()

    ## WHEN searching for the variant ID
    command = ["--database", real_db_name, "variants", "--variant-id", variant_id]
    result = runner.invoke(base_command, command)

    ## THEN the variant is printed
    assert result.exit_code == 0
    assert variant_id in result.output


def test_view_variants_region(real_mongo_adapter, real_db_name, vcf_path, ped_path):
    """Test that variants in a region are printed"""
    ## GIVEN a database with variants
    _load_case(real_mongo_adapter, vcf_path, ped_path)
    variant = real_mongo_adapter.db.variant.find_one()
    chrom, pos = variant["chrom"], variant["start"]

    runner = CliRunner()

    ## WHEN searching for variants in a region that contains the variant
    command = [
        "--database",
        real_db_name,
        "variants",
        "-c",
        chrom,
        "-s",
        str(pos),
        "-e",
        str(pos),
    ]
    result = runner.invoke(base_command, command)

    ## THEN the variant is printed
    assert result.exit_code == 0
    assert str(pos) in result.output


def test_view_variants_incomplete_region(real_mongo_adapter, real_db_name):
    """Test that a region without chromosome, start and end is rejected"""
    ## GIVEN an empty database
    runner = CliRunner()

    ## WHEN searching with a start but no chromosome
    command = ["--database", real_db_name, "variants", "-s", "100"]
    result = runner.invoke(base_command, command)

    ## THEN a warning is logged and the command succeeds
    assert result.exit_code == 0
    assert "Regions must be specified" in result.output


def test_view_sv_variants_empty(real_mongo_adapter, real_db_name, vcf_path, ped_path):
    """Test that searching for SVs in a database without SVs succeeds"""
    ## GIVEN a database with only SNVs
    _load_case(real_mongo_adapter, vcf_path, ped_path)

    runner = CliRunner()

    ## WHEN searching for SVs
    command = ["--database", real_db_name, "variants", "-t", "sv", "-c", "1"]
    result = runner.invoke(base_command, command)

    ## THEN the command succeeds and prints no variants
    assert result.exit_code == 0
    assert _stdout(result.output).strip() == ""


def test_view_index_creates_indexes(real_mongo_adapter, real_db_name):
    """Test that the index command creates indexes and --view lists them"""
    ## GIVEN an empty database
    runner = CliRunner()

    ## WHEN creating indexes
    result = runner.invoke(base_command, ["--database", real_db_name, "index"])

    ## THEN the index command succeeds and the indexes can be viewed
    assert result.exit_code == 0
    result = runner.invoke(base_command, ["--database", real_db_name, "index", "--view"])
    assert result.exit_code == 0
    assert "{" in _stdout(result.output) or "[" in _stdout(result.output)
