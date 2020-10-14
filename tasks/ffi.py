from os.path import join, exists
from subprocess import run

from faasmtools.build import (
    build_config_cmd,
    run_autotools,
    WASM_SYSROOT,
    WASM_LIB_INSTALL,
)

from invoke import task

from tasks.env import THIRD_PARTY_DIR, USABLE_CPUS, PROJ_ROOT

LIBFFI_DIR = join(THIRD_PARTY_DIR, "libffi")
LIBFFI_INSTALL_DIR = join(LIBFFI_DIR, "wasm32-unknown-wasi")


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
    src_lib = join(LIBFFI_INSTALL_DIR, ".libs", "libffi.a")
    dest_lib = join(WASM_LIB_INSTALL, "libffi.a")
    print("Copying {} to {}".format(src_lib, dest_lib))
    run("cp {} {}".format(src_lib, dest_lib), shell=True, check=True)

    # Copy header files
    header_src = join(LIBFFI_INSTALL_DIR, "include", "*")
    header_dest = join(WASM_SYSROOT, "include")
    print("Copying {} to {}".format(header_src, header_dest))
    run("cp {} {}".format(header_src, header_dest), shell=True, check=True)

    # Copy imports into place
    src_imports = join(PROJ_ROOT, "libffi.imports")
    dest_imports = join(WASM_LIB_INSTALL, "libffi.imports")
    print("Copying {} to {}".format(src_imports, dest_imports))
    run("cp {} {}".format(src_imports, dest_imports), check=True, shell=True)
