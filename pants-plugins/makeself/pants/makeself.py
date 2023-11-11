import dataclasses
import os
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Mapping, Optional

from pants.core.util_rules.external_tool import (DownloadedExternalTool,
                                                 ExternalToolRequest,
                                                 TemplatedExternalTool)
from pants.engine.env_vars import EnvironmentVars, EnvironmentVarsRequest
from pants.engine.fs import EMPTY_DIGEST, Digest
from pants.engine.platform import Platform
from pants.engine.process import Process, ProcessCacheScope
from pants.engine.rules import Get, collect_rules, rule
from pants.option.option_types import StrOption
from pants.option.subsystem import Subsystem
from pants.util.frozendict import FrozenDict
from pants.util.logging import LogLevel


class MakeselfTool(TemplatedExternalTool):
    options_scope = "makeself"
    name = "Makeself"
    help = "A tool to generate a self-extractable compressed tar archives."

    default_version = "2.5.0"
    default_known_versions = [
        "2.5.0|macos_arm64 |4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|macos_x86_64|4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|linux_arm64 |4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|linux_x86_64|4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
    ]

    default_url_template = "https://github.com/megastep/makeself/releases/download/release-{version}/makeself-{version}.run"


class MakeselfBinary:
    path: str
    immutable_input_digests: FrozenDict[str, Digest]

    def __init__(
        self,
        path: str,
        *,
        immutable_input_digests: Mapping[str, Digest],
    ) -> None:
        object.__setattr__(self, "path", path)
        object.__setattr__(
            self, "immutable_input_digests", FrozenDict(immutable_input_digests)
        )


@rule(desc="Download and configure Makeself", level=LogLevel.DEBUG)
async def setup_makeself(
    makeself_tool: MakeselfTool, platform: Platform
) -> MakeselfBinary:
    downloaded_binary = await Get(
        DownloadedExternalTool,
        ExternalToolRequest,
        makeself_tool.get_request(platform),
    )
    tool_relpath = "__makeself"
    makeself_path = os.path.join(tool_relpath, downloaded_binary.exe)
    immutable_input_digests = {tool_relpath: downloaded_binary.digest}
    return MakeselfBinary(
        path=makeself_path,
        immutable_input_digests=immutable_input_digests,
    )


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

    def __init__(
        self,
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
        object.__setattr__(self, "argv", tuple(argv))
        object.__setattr__(self, "input_digest", input_digest)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "level", level)
        object.__setattr__(self, "output_directories", tuple(output_directories or ()))
        object.__setattr__(self, "output_files", tuple(output_files or ()))
        object.__setattr__(self, "cache_scope", cache_scope)
        object.__setattr__(self, "timeout_seconds", timeout_seconds)


@rule
async def makeself_process(
    request: MakeselfProcess,
    makeself_binary: MakeselfBinary,
) -> Process:
    argv = [makeself_binary.path, *request.argv]
    return Process(
        argv,
        input_digest=request.input_digest,
        immutable_input_digests=makeself_binary.immutable_input_digests,
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
    return collect_rules()
