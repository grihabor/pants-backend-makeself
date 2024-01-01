import pytest
from makeself.pants import makeself
from makeself.pants import system_binaries as makeself_system_binaries
from makeself.pants.goals import package
from makeself.pants.goals.package import (
    BuiltMakeselfArchiveArtifact,
    MakeselfArchivePackageFieldSet,
)
from makeself.pants.makeself import RunMakeselfArchive
from makeself.pants.target_types import MakeselfArchiveTarget
from pants.core.goals.package import BuiltPackage
from pants.engine.addresses import Address
from pants.engine.process import ProcessResult
from pants.testutil.rule_runner import PYTHON_BOOTSTRAP_ENV, QueryRule, RuleRunner


@pytest.fixture
def rule_runner() -> RuleRunner:
    rule_runner = RuleRunner(
        target_types=[
            MakeselfArchiveTarget,
        ],
        rules=[
            *makeself_system_binaries.rules(),
            *package.rules(),
            *makeself.rules(),
            QueryRule(BuiltPackage, [MakeselfArchivePackageFieldSet]),
            QueryRule(ProcessResult, [RunMakeselfArchive]),
        ],
    )
    rule_runner.set_options(args=[], env_inherit=PYTHON_BOOTSTRAP_ENV)
    return rule_runner


def test_makeself_package(rule_runner: RuleRunner) -> None:
    binary_name = "archive"

    rule_runner.write_files(
        {
            "src/shell/BUILD": f"makeself_archive(name='{binary_name}', startup_script='run.sh')",
            "src/shell/run.sh": "echo test",
        }
    )
    rule_runner.chmod("src/shell/run.sh", 0o777)

    target = rule_runner.get_target(Address("src/shell", target_name=binary_name))
    field_set = MakeselfArchivePackageFieldSet.create(target)

    package = rule_runner.request(BuiltPackage, [field_set])

    assert len(package.artifacts) == 1, field_set
    assert isinstance(package.artifacts[0], BuiltMakeselfArchiveArtifact)
    relpath = f"src.shell/{binary_name}.run"
    assert package.artifacts[0].relpath == relpath

    result = rule_runner.request(
        ProcessResult,
        [
            RunMakeselfArchive(
                exe=relpath,
                description="Run built makeself archive",
                input_digest=package.digest,
            )
        ],
    )
    assert (
        result.stdout
        == b"Verifying archive integrity... All good.\nUncompressing archive.run\ntest\n"
    )
