from pants.core.goals.package import OutputPathField
from pants.engine.target import Dependencies, SingleSourceField, StringField, Target
from pants.util.strutil import help_text


class MakeselfBinaryStartupScript(SingleSourceField):
    alias = "startup_script"
    help = help_text(
        """
        Set the startup script, i.e. what gets run when executing `./my_binary.run`,
        to an address of shell source or a target that can be packaged, e.g. `pex_binary`.
        """
    )


class MakeselfBinaryDependencies(Dependencies):
    pass


class MakeselfBinaryOutputPath(OutputPathField):
    pass


class MakeselfBinaryTarget(Target):
    alias = "makeself_binary"
    core_fields = (
        MakeselfBinaryStartupScript,
        #MakeselfBinaryDependencies,
        #MakeselfBinaryOutputPath,
    )
    help = help_text(
        """
        Self-extractable archive on Unix using [makeself](https://github.com/megastep/makeself) tool.
        """
    )
