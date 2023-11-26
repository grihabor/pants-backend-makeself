import logging
import os.path
from dataclasses import dataclass

from makeself.pants.makeself import MakeselfProcess
from makeself.pants.target_types import (
    MakeselfBinaryDependencies,
    MakeselfBinaryStartupScript,
)
from pants.core.goals.package import BuiltPackage, BuiltPackageArtifact, PackageFieldSet
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.fs import CreateDigest, Digest, Directory
from pants.engine.internals.native_engine import AddPrefix, Snapshot
from pants.engine.process import ProcessResult
from pants.engine.rules import Get, MultiGet, collect_rules, rule
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
    dependencies: MakeselfBinaryDependencies


@rule
async def package_makeself_binary(
    field_set: MakeselfBinaryPackageFieldSet,
) -> BuiltPackage:
    archive_dir = "__out"

    startup_script, digest = await MultiGet(
        Get(SourceFiles, SourceFilesRequest([field_set.startup_script])),
        # Get(Targets, DependenciesRequest(field_set.dependencies)),
        Get(Digest, CreateDigest([Directory(archive_dir)])),
    )
    assert len(startup_script.files) == 1

    digest = await Get(Digest, AddPrefix(startup_script.snapshot.digest, archive_dir))

    output_filename = field_set.address.target_name
    startup_script_filename = os.path.basename(startup_script.files[0])
    result = await Get(
        ProcessResult,
        MakeselfProcess,
        MakeselfProcess.new(
            argv=[
                archive_dir,
                output_filename,
                "name of the archive",
                startup_script_filename,
            ],
            input_digest=digest,
            output_files=(output_filename,),
            description=f"Packaging Makeself binary: {field_set.address}",
        ),
    )
    snapshot = await Get(Snapshot, Digest, result.output_digest)
    # snapshot = await Get(Snapshot, Digest, digest)

    return BuiltPackage(
        snapshot.digest,
        artifacts=tuple(
            BuiltMakeselfBinaryArtifact.create(file) for file in snapshot.files
        ),
    )


def rules():
    return [
        *collect_rules(),
        UnionRule(PackageFieldSet, MakeselfBinaryPackageFieldSet),
    ]
