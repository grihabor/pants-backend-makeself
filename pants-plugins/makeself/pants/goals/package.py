import os
from pants.core.goals.package import BuiltPackage, OutputPathField, PackageFieldSet
from dataclasses import dataclass
from pants.engine.addresses import Address, Addresses
from pants.engine.fs import CreateDigest, Digest, Directory
from pants.engine.process import ProcessResult

from pants.engine.rules import Get, MultiGet, collect_rules, rule
from pants.engine.target import (
    Dependencies,
    DependenciesRequest,
    WrappedTarget,
    WrappedTargetRequest,
)
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from makeself.pants.makeself import MakeselfProcess, MakeselfTool

from makeself.pants.target_types import (
    MakeselfBinaryDependencies,
    MakeselfBinaryStartupScript,
)


@dataclass(frozen=True)
class MakeselfPackageFieldSet(PackageFieldSet):
    required_fields = (MakeselfBinaryStartupScript,)

    startup_script: MakeselfBinaryStartupScript
    dependencies: MakeselfBinaryDependencies


@rule(desc="Package self-extractable archive", level=LogLevel.INFO)
async def package_makeself_binary(
    field_set: MakeselfPackageFieldSet,
    tool: MakeselfTool,
) -> BuiltPackage:
    result_dir = "__out"

    startup_script, dependencies = await MultiGet(
        Get(Address, field_set.startup_script),
        Get(Addresses, DependenciesRequest(field_set.dependencies)),
    )

    process_output_file = os.path.join(
        result_dir, f"{field_set.address.target_name}.run"
    )

    dependencies[0].target_name
    process_result = await Get(
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
            BuiltHelmArtifact.create(file, chart.info) for file in final_snapshot.files
        ),
    )


def rules():
    return [
        *collect_rules(),
        UnionRule(PackageFieldSet, MakeselfPackageFieldSet),
    ]
