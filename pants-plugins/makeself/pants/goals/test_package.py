import os

import pytest
from makeself.pants.goals.package import BuiltMakeselfArtifact, MakeselfPackageFieldSet
from makeself.pants.goals.package import rules as makeself_package_rules
from makeself.pants.makeself import MakeselfBinary
from makeself.pants.makeself import rules as makeself_rules
from makeself.pants.target_types import MakeselfBinaryTarget
from pants.core.goals.package import BuiltPackage
from pants.engine.addresses import Address
from pants.engine.rules import QueryRule
from pants.testutil.rule_runner import QueryRule, RuleRunner


@pytest.fixture
def rule_runner() -> RuleRunner:
    rule_runner = RuleRunner(
        target_types=[
            MakeselfBinaryTarget,
        ],
        rules=[
            *makeself_package_rules(),
            *makeself_rules(),
            QueryRule(MakeselfBinary, ()),
        ],
    )
    return rule_runner


def _assert_build_package(rule_runner: RuleRunner, *, binary_name: str) -> None:
    target = rule_runner.get_target(Address("src/shell", target_name=binary_name))
    field_set = MakeselfPackageFieldSet.create(target)

    dest_dir = field_set.output_path.value_or_default(file_ending=None)
    result = rule_runner.request(BuiltPackage, [field_set])

    assert len(result.artifacts) == 1
    assert isinstance(result.artifacts[0], BuiltMakeselfArtifact)
    assert result.artifacts[0].relpath == os.path.join(dest_dir, "bla")
    assert result.artifacts[0].info


def test_makeself_package(rule_runner: RuleRunner) -> None:
    binary_name = "foo"

    rule_runner.write_files(
        {
            "src/shell/BUILD": f"makeself_binary(name='{binary_name}', startup_script='run.sh')",
            "src/shell/run.sh": "echo test",
        }
    )

    _assert_build_package(rule_runner, binary_name=binary_name)
