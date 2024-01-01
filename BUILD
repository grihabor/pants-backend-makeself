python_sources(name="py-src")

pex_binary(name="pex", entry_point="hello.py")

shell_source(name="sh-src", source="hello.sh", dependencies=[":pex"])

makeself_archive(
    name="hello",
    startup_script="hello.sh",
    packages=[":pex"],
)
