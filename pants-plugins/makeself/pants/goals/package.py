import logging
from dataclasses import dataclass

from pants.core.goals.package import BuiltPackage, BuiltPackageArtifact, PackageFieldSet
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.env_vars import EnvironmentVars, EnvironmentVarsRequest
from pants.engine.fs import CreateDigest, Digest, DigestContents, FileContent
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.unions import UnionRule

from makeself.pants.target_types import MakeselfBinaryStartupScript

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuiltMakeselfBinaryArtifact(BuiltPackageArtifact):
    @classmethod
    def create(cls, relpath: str) -> "BuiltMakeselfBinaryArtifact":
        return cls(
            relpath=relpath,
            extra_log_lines=(f"Built makeself binary: {relpath}",),
        )


@dataclass(frozen=True)
class MakeselfBinaryPackageFieldSet(PackageFieldSet):
    required_fields = (MakeselfBinaryStartupScript,)

    startup_script: MakeselfBinaryStartupScript


@rule
async def package_makeself_binary(
    field_set: MakeselfBinaryPackageFieldSet,
) -> BuiltPackage:
    """Substitute env vars in k8s source"""
    source_files = await Get(
        SourceFiles,
        SourceFilesRequest([field_set.source]),
    )
    files = await Get(DigestContents, Digest, source_files.snapshot.digest)
    assert len(files) == 1
    file_content = files[0]
    logger.debug("k8s source %s", file_content)
    rendered_path = file_content.path + ".rendered"

    # TODO use options_env_aware
    env = await Get(
        EnvironmentVars,
        EnvironmentVarsRequest,
        EnvironmentVarsRequest(requested=["VERSION"]),
    )
    logger.debug("env %s", env)
    rendered_content = (
        file_content.content.decode("utf-8").format(**env).encode("utf-8")
    )
    digest = await Get(
        Digest, CreateDigest([FileContent(rendered_path, rendered_content)])
    )

    return BuiltPackage(digest, (BuiltMakeselfBinaryArtifact.create(rendered_path),))


def rules():
    return [
        *collect_rules(),
        UnionRule(PackageFieldSet, MakeselfBinaryPackageFieldSet),
    ]
