import json

from click.testing import CliRunner

from loqusdb.commands.cli import cli as base_command

NR_MEIS = 18


def _invoke(db_name, *args):
    result = CliRunner().invoke(base_command, ["--database", db_name, *args])
    assert result.exit_code == 0, result.output
    return result.output


def _load(db_name, mei_vcf_path, ped_path):
    _invoke(db_name, "load", "--mei-variants", mei_vcf_path, "-f", ped_path)


def test_load_and_count_mei_case(real_mongo_adapter, real_db_name, mei_vcf_path, ped_path):
    ## WHEN loading a MEI VCF via the CLI
    _load(real_db_name, mei_vcf_path, ped_path)
    ## THEN the case is counted as a MEI case, not an SV case
    assert _invoke(real_db_name, "cases", "--count", "-t", "mei").splitlines()[-1] == "1"
    assert _invoke(real_db_name, "cases", "--count", "-t", "sv").splitlines()[-1] == "0"
    assert real_mongo_adapter.db.mei_variant.count_documents({}) == NR_MEIS


def test_view_mei_variant_json(real_mongo_adapter, real_db_name, mei_vcf_path, ped_path):
    ## GIVEN a database with MEIs
    _load(real_db_name, mei_vcf_path, ped_path)
    ## WHEN querying a single MEI the way Scout queries SVs, slightly off the breakpoint
    output = _invoke(
        real_db_name,
        "variants",
        "--to-json",
        "--variant-id",
        "1_21898461_A_<INS:ME>",
        "--case-count",
        "-t",
        "mei",
        "-c",
        "1",
        "-s",
        "21898461",
        "-e",
        "21898461",
        "--sv-type",
        "ALU",
    )
    ## THEN the cluster is returned with observations and the number of MEI cases
    variant = json.loads(output.strip().splitlines()[-1])
    assert variant["observations"] == 1
    assert variant["sv_type"] == "INS:ME:ALU"
    assert variant["total"] == 1


def _export_records(db_name, outfile, *args):
    _invoke(db_name, "export", "-t", "mei", "--freq", "-o", str(outfile), *args)
    lines = outfile.read_text().splitlines()
    return lines, [line.split("\t") for line in lines if not line.startswith("#")]


def test_export_meis(real_mongo_adapter, real_db_name, mei_vcf_path, ped_path, tmp_path):
    ## GIVEN a database with ALU and L1 insertions
    _load(real_db_name, mei_vcf_path, ped_path)
    ## WHEN exporting all MEIs
    lines, records = _export_records(real_db_name, tmp_path / "meis.vcf")
    ## THEN all clusters are exported as generic MEIs, with the element in MEINFO
    assert '##ALT=<ID=INS:ME,Description="Insertion of a mobile element">' in lines
    assert len(records) == NR_MEIS
    assert {record[4] for record in records} == {"<INS:ME>"}
    elements = {info.split("MEINFO=")[1].split(",")[0] for *_, info in records}
    assert elements == {"ALU", "L1"}


def test_export_meis_per_element(
    real_mongo_adapter, real_db_name, mei_vcf_path, ped_path, tmp_path
):
    ## GIVEN a database with ALU and L1 insertions
    _load(real_db_name, mei_vcf_path, ped_path)
    ## WHEN exporting one element, given in lower case
    lines, records = _export_records(real_db_name, tmp_path / "alu.vcf", "--mei-type", "alu")
    ## THEN only that element is exported
    assert "##MEIType=INS:ME:ALU" in lines
    assert 0 < len(records) < NR_MEIS
    assert all(record[7].endswith("MEINFO=ALU,.,.,.") for record in records)


def test_export_mei_type_requires_mei(real_mongo_adapter, real_db_name):
    ## WHEN using --mei-type for another variant type
    result = CliRunner().invoke(
        base_command, ["--database", real_db_name, "export", "--mei-type", "ALU"]
    )
    ## THEN the export is aborted
    assert result.exit_code == 1


def test_annotate_meis(real_mongo_adapter, real_db_name, mei_vcf_path, ped_path):
    ## GIVEN a database with MEIs
    _load(real_db_name, mei_vcf_path, ped_path)
    ## WHEN annotating the MEI VCF
    output = _invoke(real_db_name, "annotate", "--mei", mei_vcf_path)
    # Log lines are mixed into the output, so pick out the VCF records
    records = [line for line in output.splitlines() if len(line.split("\t")) >= 8]
    records = [line for line in records if not line.startswith("#")]
    ## THEN every record has an observation count
    assert len(records) == NR_MEIS
    assert all("Obs=1" in record for record in records)
    assert "##NrCases=1" in output


def test_delete_mei_case(real_mongo_adapter, real_db_name, mei_vcf_path, ped_path, case_id):
    ## GIVEN a database with MEIs
    _load(real_db_name, mei_vcf_path, ped_path)
    ## WHEN deleting the case
    _invoke(real_db_name, "delete", "-c", case_id)
    ## THEN the MEIs are removed
    assert real_mongo_adapter.db.mei_variant.count_documents({}) == 0
