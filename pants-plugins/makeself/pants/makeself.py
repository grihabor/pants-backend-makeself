import dataclasses
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Optional

from makeself.pants.system_binaries import (AwkBinary, BasenameBinary,
                                            CutBinary, DfBinary, DirnameBinary,
                                            ExprBinary, FindBinary, GzipBinary,
                                            HeadBinary, IdBinary, Md5sumBinary,
                                            SedBinary, TailBinary, WcBinary)
from pants.core.util_rules import external_tool
from pants.core.util_rules.external_tool import (DownloadedExternalTool,
                                                 ExternalToolRequest,
                                                 TemplatedExternalTool)
from pants.core.util_rules.system_binaries import (BashBinary, BinaryShims,
                                                   BinaryShimsRequest,
                                                   CatBinary, MkdirBinary)
from pants.engine.fs import EMPTY_DIGEST, Digest, MergeDigests
from pants.engine.platform import Platform
from pants.engine.process import Process, ProcessCacheScope, ProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)


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


class MakeselfDistribution(DownloadedExternalTool):
    """The Makeself distribution."""


@rule(desc="Download Makeself distribution", level=LogLevel.DEBUG)
async def download_makeself_distrubution(
    options: MakeselfSubsystem,
    platform: Platform,
) -> MakeselfDistribution:
    tool = await Get(
        DownloadedExternalTool,
        ExternalToolRequest,
        options.get_request(platform),
    )
    logger.debug("makeself external tool: %s", tool)
    return MakeselfDistribution(digest=tool.digest, exe=tool.exe)


class MakeselfBinary(DownloadedExternalTool):
    """The Makeself binary."""


@rule(desc="Extract Makeself Binary", level=LogLevel.DEBUG)
async def extract_makeself_binary(
    dist: MakeselfDistribution,
    awk: AwkBinary,
    basename: BasenameBinary,
    bash: BashBinary,
    cat: CatBinary,
    cut: CutBinary,
    df: DfBinary,
    dirname: DirnameBinary,
    expr: ExprBinary,
    gzip: GzipBinary,
    head: HeadBinary,
    id: IdBinary,
    mkdir: MkdirBinary,
    sed: SedBinary,
    tail: TailBinary,
    wc: WcBinary,
    find: FindBinary,
    md5sum: Md5sumBinary,
) -> MakeselfBinary:
    out = "__makeself"
    shims = await Get(
        BinaryShims,
        BinaryShimsRequest(
            paths=(
                awk,
                basename,
                bash,
                cat,
                cut,
                df,
                dirname,
                expr,
                gzip,
                head,
                id,
                mkdir,
                sed,
                tail,
                wc,
                find,
                md5sum,
            ),
            rationale="execute makeself script",
        ),
    )
    digest = await Get(Digest, MergeDigests([dist.digest, shims.digest]))
    result = await Get(
        ProcessResult,
        Process(
            argv=[bash.path, "-c", f"md5sum {dist.exe}; {dist.exe} --check"],
            # [
            #    dist.exe,
            #    "--nox11",
            #    "--nochown",
            #    "--target",
            #    out,
            # ],
            # [
            # bash.path,
            # "-c",
            # f"find {out}; {dist.exe} --check; {dist.exe} --nox11 --nochown --target {out}",
            # ]
            input_digest=digest,
            output_directories=[out],
            description=f"Extracting Makeself binary: {out}",
        ),
    )
    return MakeselfBinary(digest=result.output_digest, exe=f"{out}/makeself.sh")


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
    def new(
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
    makeself: MakeselfBinary,
    bash: BashBinary,
) -> Process:
    argv = [bash.path, "-c", " ".join([makeself.exe, *request.argv])]
    return Process(
        argv,
        input_digest=request.input_digest,
        immutable_input_digests={makeself.exe: makeself.digest},
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
