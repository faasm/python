from os.path import join, exists
from subprocess import run

from tasks.env import USABLE_CPUS

from faasmcli.util.toolchain import (
    WASM_CC,
    WASM_BUILD,
    WASM_HOST,
    BASE_CONFIG_CMD,
    WASM_CFLAGS_SHARED,
    WASM_LDFLAGS_SHARED,
)

from invoke import task

from os import makedirs

from tasks.env import THIRD_PARTY_DIR 
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

    # Configure
    configure_cmd = ["./configure"]
    configure_cmd.extend(BASE_CONFIG_CMD)
    configure_cmd.extend(
        [
            "LD={}".format(WASM_CC),
            'LDFLAGS="{}"'.format(" ".join(WASM_LDFLAGS_SHARED)),
            "--build={}".format(WASM_BUILD),
            "--host={}".format(WASM_HOST),
            "--prefix={}".format(PREFIX),
        ]
    )

    run(" ".join(configure_cmd), check=True, shell=True, cwd=LIBFFI_DIR)
