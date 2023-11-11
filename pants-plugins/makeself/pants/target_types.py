from pants.backend.shell.target_types import ShellSourceField
from pants.engine.target import Dependencies, Field, StringField, Target
from pants.util.strutil import help_text


class MakeselfBinaryStartupScript(StringField):
    alias = "startup_script"
    default = None
    help = help_text(
        """
        Set the startup script, i.e. what gets run when executing `./my_binary.run`,
        to an address of shell source or a target that can be packaged, e.g. `pex_binary`.
        """
    )


class MakeselfBinaryDependencies(Dependencies):
    pass


class MakeselfBinaryTarget(Target):
    alias = "makeself_binary"
    core_fields = (
        MakeselfBinaryStartupScript,
        MakeselfBinaryDependencies,
    )
    help = help_text(
        f"""
        Self-extractable archive on Unix using [makeself](https://github.com/megastep/makeself) tool.
        """
    )
