from os.path import join, exists
from subprocess import run

from faasmcli.util.toolchain import (
    build_config_cmd,
    run_autotools,
)

from invoke import task

from os import makedirs

from tasks.env import THIRD_PARTY_DIR, USABLE_CPUS

LIBFFI_DIR = join(THIRD_PARTY_DIR, "libffi")
PREFIX = join(LIBFFI_DIR, "install")


@task(default=True)
def build(ctx, clean=False):
    """
    Builds libffi
    """
    if exists(join(LIBFFI_DIR, "Makefile")) and clean:
        run("make clean", cwd=LIBFFI_DIR, shell=True, check=True)

    if not exists(PREFIX):
        makedirs(PREFIX)

    # Autotools
    run_autotools(LIBFFI_DIR)

    # Configure
    configure_cmd = build_config_cmd(
        [
            "./configure",
            "--prefix={}".format(PREFIX),
            "--disable-multi-os-directory",
            "--disable-docs",
        ],
        shared=True,
    )
    configure_cmd = " ".join(configure_cmd)
    run(configure_cmd, check=True, shell=True, cwd=LIBFFI_DIR)

    # Run make
    make_cmd = ["make", "-j {}".format(USABLE_CPUS)]
    run(" ".join(make_cmd), shell=True, check=True, cwd=LIBFFI_DIR)
