from os.path import join, exists
from subprocess import run

from faasmcli.util.toolchain import (
    BASE_CONFIG_CMD,
    BASE_CONFIG_FLAGS_SHARED,
    build_config_cmd,
)

from invoke import task

from os import makedirs

from tasks.env import THIRD_PARTY_DIR

LIBFFI_DIR = join(THIRD_PARTY_DIR, "libffi")
PREFIX = join(LIBFFI_DIR, "install")


@task
def autoconf(ctx):
    """
    Runs autoconf on libffi
    """
    autoconf_cmd = build_config_cmd([
            "autoconf",
            ])

    run(" ".join(autoconf_cmd), shell=True, check=True, cwd=LIBFFI_DIR)


@task(default=True)
def build(ctx, clean=False):
    """
    Builds libffi
    """
    if exists(join(LIBFFI_DIR, "Makefile")) and clean:
        run("make clean", cwd=LIBFFI_DIR, shell=True, check=True)

    if not exists(PREFIX):
        makedirs(PREFIX)

    # Configure
    configure_cmd = ["./configure"]
    configure_cmd.extend(BASE_CONFIG_CMD)
    configure_cmd.extend(BASE_CONFIG_FLAGS_SHARED)
    configure_cmd.extend(
        [
            "--prefix={}".format(PREFIX),
        ]
    )

    run(" ".join(configure_cmd), check=True, shell=True, cwd=LIBFFI_DIR)
