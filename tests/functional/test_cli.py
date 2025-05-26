from click.testing import CliRunner

from loqusdb.commands.cli import cli as base_command
from loqusdb.exceptions import ProfileError


def test_base_command():
    runner = CliRunner()
    result = runner.invoke(base_command, ["--help"])

    assert result.exit_code == 0


def test_load_command(vcf_path, ped_path, real_mongo_adapter, real_db_name):
    ## GIVEN a vcf_path a ped_path and a empty database
    assert sum([1 for case in real_mongo_adapter.cases()]) == 0
    runner = CliRunner()
    ## WHEN inserting a case via the CLI
    command = ["--database", real_db_name, "load", "--variant-file", vcf_path, "-f", ped_path]
    result = runner.invoke(base_command, command)
    ## THEN assert that the cli exits without problems
    assert result.exit_code == 0
    ## THEN assert that the case was added
    assert sum([1 for case in real_mongo_adapter.cases()]) == 1


def test_load_command_no_ped_case_id(vcf_path, case_id, real_mongo_adapter, real_db_name):
    ## GIVEN a vcf_path a ped_path and a empty database
    assert real_mongo_adapter.case({"case_id": case_id}) is None
    runner = CliRunner()
    ## WHEN inserting a case via the CLI
    command = ["--database", real_db_name, "load", "--variant-file", vcf_path, "-c", case_id]
    result = runner.invoke(base_command, command)
    ## THEN assert that the cli exits without problems
    assert result.exit_code == 0
    ## THEN assert that the case was added
    assert real_mongo_adapter.case({"case_id": case_id})


def test_load_command_no_ped(vcf_path, ped_path, real_mongo_adapter, real_db_name):
    ## GIVEN a vcf_path a ped_path and a empty database
    runner = CliRunner()
    ## WHEN inserting a case via the CLI without a ped file
    command = ["--database", real_db_name, "load", "--variant-file", vcf_path]
    result = runner.invoke(base_command, command)

    ## THEN assert that the cli exits with code 1
    assert result.exit_code == 1


def test_load_command_check_profile(
    zipped_vcf_path, ped_path, real_mongo_adapter, real_db_name, profile_vcf_path
):
    NEW_CASE_NAME = "other_case"
    # Load profile variants
    runner = CliRunner()
    command = ["--database", real_db_name, "profile", "--load", "--variant-file", profile_vcf_path]
    result = runner.invoke(base_command, command)

    # WHEN load command with --check-profile flag
    command = [
        "--database",
        real_db_name,
        "load",
        "--variant-file",
        zipped_vcf_path,
        "-f",
        ped_path,
        "--check-profile",
        zipped_vcf_path,
    ]
    result = runner.invoke(base_command, command)
    ## THEN assert that the cli exits without problems
    assert result.exit_code == 0
    ## THEN assert if field 'profile is found in the individual documents'
    for case in real_mongo_adapter.cases():
        for individual in case["individuals"]:
            assert individual.get("profile")

    ##WHEN load the same case (change case-id with -c option)
    command = [
        "--database",
        real_db_name,
        "load",
        "--variant-file",
        zipped_vcf_path,
        "-f",
        ped_path,
        "--check-profile",
        zipped_vcf_path,
        "-c",
        "other_case",
    ]
    result = runner.invoke(base_command, command)
    ## THEN assert that exit_code is not 0 and error is raised
    assert result.exit_code != 0
    assert type(result.exception) == ProfileError

    ##WHEN try to insert the same case without --check-profile flag (should work)
    command = [
        "--database",
        real_db_name,
        "load",
        "--variant-file",
        zipped_vcf_path,
        "-f",
        ped_path,
        "-c",
        NEW_CASE_NAME,
    ]
    result = runner.invoke(base_command, command)
    ## THEN assert that exit_code is 0
    assert result.exit_code == 0
    ## THEN assert that no profile string is added to the individuals
    for individual in real_mongo_adapter.case({"case_id": NEW_CASE_NAME})["individuals"]:
        assert not individual.get("profile")


def test_load_profile_command(profile_vcf_path, real_mongo_adapter, real_db_name):
    runner = CliRunner()

    command = ["--database", real_db_name, "profile", "--load", "--variant-file", profile_vcf_path]
    result = runner.invoke(base_command, command)

    assert result.exit_code == 0
    assert len(list(real_mongo_adapter.profile_variants())) > 0


def test_delete_command_family_file(vcf_path, ped_path, real_mongo_adapter, real_db_name):
    ## GIVEN a vcf_path a ped_path and a empty database
    runner = CliRunner()
    assert sum([1 for case in real_mongo_adapter.cases()]) == 0

    ## WHEN inserting a case via the CLI without a ped file
    load_command = ["--database", real_db_name, "load", "--variant-file", vcf_path, "-f", ped_path]
    result = runner.invoke(base_command, load_command)
    ## THEN assert that the case was added
    assert sum(1 for case in real_mongo_adapter.cases()) == 1

    ## WHEN deleting the case a case via the CLI without a ped file
    delete_command = ["--database", real_db_name, "delete", "-f", ped_path]
    result = runner.invoke(base_command, delete_command)

    ## THEN assert that the cli exits without problems
    assert result.exit_code == 0
    ## THEN assert that the case was deleted
    assert sum(1 for case in real_mongo_adapter.cases()) == 0


def test_delete_command_case_id(vcf_path, case_id, real_mongo_adapter, real_db_name):
    ## GIVEN a vcf_path a ped_path and a empty database
    runner = CliRunner()
    assert real_mongo_adapter.case({"case_id": case_id}) is None

    ## WHEN inserting a case via the CLI without a ped file
    load_command = ["--database", real_db_name, "load", "--variant-file", vcf_path, "-c", case_id]
    result = runner.invoke(base_command, load_command)
    ## THEN assert that the case was added
    assert isinstance(real_mongo_adapter.case({"case_id": case_id}), dict)

    ## WHEN deleting the case a case via the CLI without a ped file
    delete_command = ["--database", real_db_name, "delete", "-c", case_id]
    result = runner.invoke(base_command, delete_command)

    ## THEN assert that the cli exits without problems
    assert result.exit_code == 0
    ## THEN assert that the case was deleted
    assert real_mongo_adapter.case({"case_id": case_id}) is None


def test_cases_command_case_id(vcf_path, case_id, real_mongo_adapter, real_db_name):
    ## GIVEN a vcf_path a ped_path and a empty database
    runner = CliRunner()
    assert real_mongo_adapter.case({"case_id": case_id}) is None

    ## WHEN inserting a case via the CLI without a ped file
    load_command = ["--database", real_db_name, "load", "--variant-file", vcf_path, "-c", case_id]
    result = runner.invoke(base_command, load_command)
    ## THEN assert that the case was added
    assert isinstance(real_mongo_adapter.case({"case_id": case_id}), dict)

    ## WHEN searching for the case with CLI
    command = ["--database", real_db_name, "cases", "--case-id", case_id]
    result = runner.invoke(base_command, command)

    ## THEN assert that the cli exits without problems
    assert result.exit_code == 0


def test_cases_command_non_existing(vcf_path, case_id, real_mongo_adapter, real_db_name):
    ## GIVEN a vcf_path a ped_path and a empty database
    runner = CliRunner()
    assert real_mongo_adapter.case({"case_id": case_id}) is None

    ## WHEN searching for a non existing case
    command = ["--database", real_db_name, "cases", "--case-id", "hello"]
    result = runner.invoke(base_command, command)

    ## THEN assert that the exit is zero
    assert result.exit_code == 0
    # Exit code should be 0 even if there is no result returned


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
