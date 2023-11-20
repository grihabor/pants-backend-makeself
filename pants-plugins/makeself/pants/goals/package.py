import os
from dataclasses import dataclass

from pants.core.util_rules.environments import EnvironmentName

from makeself.pants.makeself import MakeselfBinary, MakeselfProcess
from makeself.pants.target_types import (
    MakeselfBinaryDependencies,
    MakeselfBinaryOutputPath,
    MakeselfBinaryStartupScript,
)
from pants.core.goals.package import BuiltPackage, BuiltPackageArtifact, PackageFieldSet
from pants.core.goals.package import BuiltPackage, BuiltPackageArtifact, PackageFieldSet
from pants.engine.addresses import Address, Addresses
from pants.engine.process import ProcessResult
from pants.engine.rules import Get, MultiGet, collect_rules, rule
from pants.engine.target import DependenciesRequest
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel


@dataclass(frozen=True)
class BuiltMakeselfArtifact(BuiltPackageArtifact):
    @classmethod
    def create(cls, relpath: str) -> "BuiltMakeselfArtifact":
        return cls(
            relpath=relpath,
            extra_log_lines=(f"Built Makeself chart artifact: {relpath}",),
        )


@dataclass(frozen=True)
class MakeselfPackageFieldSet(PackageFieldSet):
    required_fields = (MakeselfBinaryStartupScript,)

    startup_script: MakeselfBinaryStartupScript
    #dependencies: MakeselfBinaryDependencies
    output_path: MakeselfBinaryOutputPath


@rule#(desc="Package self-extractable archive", level=LogLevel.INFO)
async def package_makeself_binary(
    field_set: MakeselfPackageFieldSet,
    tool: MakeselfBinary,
    #_: EnvironmentName,
) -> BuiltPackage:
    result_dir = "__out"
    raise RuntimeError

    startup_script, dependencies = await MultiGet(
        Get(Address, field_set.startup_script),
        Get(Addresses, DependenciesRequest(field_set.dependencies)),
    )

    process_output_file = os.path.join(
        result_dir, f"{field_set.address.target_name}.run"
    )

    dependencies[0].target_name
    await Get(
        ProcessResult,
        MakeselfProcess(
            argv=[archive_dir, file_name, label, startup_script],
            input_digest=result_digest,
            output_files=(process_output_file,),
            description=f"Packaging Makeself binary: {field_set.address}",
        ),
    )

    return BuiltPackage(
        final_snapshot.digest,
        artifacts=tuple(
            BuiltMakeselfArtifact.create(file) for file in final_snapshot.files
        ),
    )


def rules():
    return [
        *collect_rules(),
        UnionRule(PackageFieldSet, MakeselfPackageFieldSet),
    ]
