import logging
import os.path
from dataclasses import dataclass
from pathlib import PurePath

from makeself.pants.makeself import MakeselfProcess
from makeself.pants.target_types import (
    MakeselfBinaryFilesField,
    MakeselfBinaryPackagesField,
    MakeselfBinaryStartupScript,
)
from pants.core.goals.package import (
    BuiltPackage,
    BuiltPackageArtifact,
    EnvironmentAwarePackageRequest,
    OutputPathField,
    PackageFieldSet,
)
from pants.core.target_types import FileSourceField
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.addresses import UnparsedAddressInputs
from pants.engine.fs import Digest, MergeDigests
from pants.engine.internals.native_engine import AddPrefix, Snapshot
from pants.engine.process import ProcessResult
from pants.engine.rules import Get, MultiGet, collect_rules, rule
from pants.engine.target import (
    FieldSetsPerTarget,
    FieldSetsPerTargetRequest,
    HydratedSources,
    HydrateSourcesRequest,
    SourcesField,
    Targets,
)
from pants.engine.unions import UnionRule

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuiltMakeselfBinaryArtifact(BuiltPackageArtifact):
    @classmethod
    def create(cls, relpath: str) -> "BuiltMakeselfBinaryArtifact":
        return cls(
            relpath=relpath,
            extra_log_lines=(f"Built Makeself binary: {relpath}",),
        )


@dataclass(frozen=True)
class MakeselfBinaryPackageFieldSet(PackageFieldSet):
    required_fields = (MakeselfBinaryStartupScript,)

    startup_script: MakeselfBinaryStartupScript
    files: MakeselfBinaryFilesField
    packages: MakeselfBinaryPackagesField
    output_path: OutputPathField


@rule
async def package_makeself_binary(
    field_set: MakeselfBinaryPackageFieldSet,
) -> BuiltPackage:
    archive_dir = "__archive"

    package_targets, file_targets = await MultiGet(
        Get(Targets, UnparsedAddressInputs, field_set.packages.to_unparsed_address_inputs()),
        Get(Targets, UnparsedAddressInputs, field_set.files.to_unparsed_address_inputs()),
    )

    package_field_sets_per_target = await Get(
        FieldSetsPerTarget, FieldSetsPerTargetRequest(PackageFieldSet, package_targets)
    )
    packages = await MultiGet(
        Get(BuiltPackage, EnvironmentAwarePackageRequest(field_set))
        for field_set in package_field_sets_per_target.field_sets
    )

    file_sources = await MultiGet(
        Get(
            HydratedSources,
            HydrateSourcesRequest(
                tgt.get(SourcesField),
                for_sources_types=(FileSourceField,),
                enable_codegen=True,
            ),
        )
        for tgt in file_targets
    )

    startup_script = await Get(SourceFiles, SourceFilesRequest([field_set.startup_script]))
    assert len(startup_script.files) == 1

    input_digest = await Get(
        Digest,
        MergeDigests(
            (
                startup_script.snapshot.digest,
                *(package.digest for package in packages),
                *(sources.snapshot.digest for sources in file_sources),
            )
        ),
    )
    input_digest = await Get(Digest, AddPrefix(input_digest, archive_dir))

    output_filename = PurePath(field_set.output_path.value_or_default(file_ending="run"))
    startup_script_filename = os.path.basename(startup_script.files[0])
    result = await Get(
        ProcessResult,
        MakeselfProcess,
        MakeselfProcess.new(
            archive_dir=archive_dir,
            file_name=output_filename.name,
            label="name of the archive",
            startup_script=startup_script_filename,
            input_digest=input_digest,
            output_filename=str(output_filename),
            description=f"Packaging Makeself binary: {field_set.address}",
        ),
    )
    digest = await Get(Digest, AddPrefix(result.output_digest, str(output_filename.parent)))
    snapshot = await Get(Snapshot, Digest, digest)

    return BuiltPackage(
        snapshot.digest,
        artifacts=tuple(BuiltMakeselfBinaryArtifact.create(file) for file in snapshot.files),
    )


def rules():
    return [
        *collect_rules(),
        UnionRule(PackageFieldSet, MakeselfBinaryPackageFieldSet),
    ]
