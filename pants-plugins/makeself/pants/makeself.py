import dataclasses
import os
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Mapping, Optional

from pants.core.util_rules import external_tool
from pants.core.util_rules.external_tool import (
    DownloadedExternalTool,
    ExternalToolRequest,
    TemplatedExternalTool,
)
from pants.engine import process
from pants.engine.fs import EMPTY_DIGEST, Digest
from pants.engine.platform import Platform
from pants.engine.process import Process, ProcessCacheScope
from pants.engine.rules import Get, collect_rules, rule
from pants.util.frozendict import FrozenDict
from pants.util.logging import LogLevel

from makeself.pants.target_types import MakeselfBinaryDependencies


class MakeselfSubsystem(TemplatedExternalTool):
    options_scope = "makeself"
    help = "A tool to generate a self-extractable compressed tar archives."

    default_version = "2.5.0"
    default_known_versions = [
        "2.5.0|macos_arm64 |4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|macos_x86_64|4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|linux_arm64 |4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|linux_x86_64|4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
    ]

    default_url_template = "https://github.com/megastep/makeself/releases/download/release-{version}/makeself-{version}.run"


class MakeselfBinary(DownloadedExternalTool):
    """The Makeself binary."""


@rule(desc="Download Makeself binary", level=LogLevel.DEBUG)
async def download_makeself(
    options: MakeselfSubsystem, platform: Platform
) -> MakeselfBinary:
    binary = await Get(
        DownloadedExternalTool,
        ExternalToolRequest,
        options.get_request(platform),
    )
    return MakeselfBinary(digest=binary.digest, exe=binary.exe)


@dataclass(frozen=True)
class MakeselfProcess:
    argv: tuple[str, ...]
    input_digest: Digest
    description: str = dataclasses.field(compare=False)
    level: LogLevel
    cache_scope: Optional[ProcessCacheScope]
    timeout_seconds: Optional[int]
    output_directories: tuple[str, ...]
    output_files: tuple[str, ...]

    @classmethod
    def from_(
        cls,
        argv: Iterable[str],
        *,
        description: str,
        input_digest: Digest = EMPTY_DIGEST,
        level: LogLevel = LogLevel.INFO,
        output_directories: Optional[Iterable[str]] = None,
        output_files: Optional[Iterable[str]] = None,
        cache_scope: Optional[ProcessCacheScope] = None,
        timeout_seconds: Optional[int] = None,
    ):
        return MakeselfProcess(
            argv=tuple(argv),
            input_digest=input_digest,
            description=description,
            level=level,
            output_directories=tuple(output_directories or ()),
            output_files=tuple(output_files or ()),
            cache_scope=cache_scope,
            timeout_seconds=timeout_seconds,
        )


@rule
async def makeself_process(
    request: MakeselfProcess,
    binary: MakeselfBinary,
) -> Process:
    argv = [binary.path, *request.argv]
    return Process(
        argv,
        input_digest=request.input_digest,
        immutable_input_digests=binary.immutable_input_digests,
        env={},
        description=request.description,
        level=request.level,
        append_only_caches={},
        output_directories=request.output_directories,
        output_files=request.output_files,
        cache_scope=request.cache_scope or ProcessCacheScope.SUCCESSFUL,
        timeout_seconds=request.timeout_seconds,
    )


def rules():
    return [
        *collect_rules(),
        *external_tool.rules(),
    ]
