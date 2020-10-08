from os.path import join, exists
from subprocess import run

from faasmcli.util.toolchain import (
    build_config_cmd,
    run_autotools,
    WASM_SYSROOT,
    WASM_LIB_INSTALL,
)

from invoke import task

from tasks.env import THIRD_PARTY_DIR, USABLE_CPUS

LIBFFI_DIR = join(THIRD_PARTY_DIR, "libffi")


@task(default=True)
def build(ctx, clean=False):
    """
    Builds libffi
    """
    if exists(join(LIBFFI_DIR, "Makefile")) and clean:
        run("make clean", cwd=LIBFFI_DIR, shell=True, check=True)

    # Autotools
    run_autotools(LIBFFI_DIR)

    # Configure
    configure_cmd = build_config_cmd(
        [
            "./configure",
            "--prefix={}".format(WASM_SYSROOT),
            "--disable-multi-os-directory",
            "--disable-docs",
        ],
    )
    configure_cmd = " ".join(configure_cmd)
    run(configure_cmd, check=True, shell=True, cwd=LIBFFI_DIR)

    # Run make
    make_cmd = ["make", "-j {}".format(USABLE_CPUS)]
    run(" ".join(make_cmd), shell=True, check=True, cwd=LIBFFI_DIR)

    # Run install (although apparently doesn't do anything)
    run("make install", shell=True, check=True, cwd=LIBFFI_DIR)

    # Ensure the lib is copied into place
    src_lib = join(LIBFFI_DIR, "wasm32-unknown-wasi", ".libs", "libffi.a")
    dest_lib = join(WASM_LIB_INSTALL, "libffi.a")
    print("Copying {} to {}".format(src_lib, dest_lib))
    run("cp {} {}".format(src_lib, dest_lib), shell=True, check=True) 

