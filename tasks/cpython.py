import os

from copy import copy
from tasks.env import PROJ_ROOT, USABLE_CPUS
from os.path import join, exists
from subprocess import run

from faasmcli.util.toolchain import (
    WASM_CC,
    WASM_CPP,
    WASM_AR,
    WASM_CXX,
    WASM_RANLIB,
    WASM_BUILD,
    WASM_CFLAGS,
    WASM_HOST,
)

from invoke import task

# The python library name might have a letter at the end of it,
# e.g. for a debug build it'll be libpython3.8d.a and with
# pymalloc it'll be libpython3.8m.a
LIBPYTHON_NAME = "libpython3.8.a"

# We need to have a version of Python installed on the host with _exactly_
# the same version as the one we're building
BUILD_PYTHON_BIN = "/usr/local/faasm/python3.8/bin"
BUILD_PYTHON_EXE = join(BUILD_PYTHON_BIN, "python3.8")
BUILD_PYTHON_PIP = join(BUILD_PYTHON_BIN, "pip3.8")

# CPython src
CPYTHON_SRC = join(PROJ_ROOT, "third-party", "cpython")
CPYTHON_BUILD_DIR = join(CPYTHON_SRC, "build", "wasm")

# CPython install
INSTALL_DIR = join(CPYTHON_SRC, "install", "wasm")
WASM_PYTHON = join(INSTALL_DIR, "bin", "python3.8")
WASM_PYTHON_INCLUDES = join(INSTALL_DIR, "include")

# Environment variables
ENV_VARS = copy(os.environ)
PATH_ENV_VAR = ENV_VARS.get("PATH", "")
PATH_ENV_VAR = "{}:{}".format(BUILD_PYTHON_BIN, PATH_ENV_VAR)
ENV_VARS.update(
    {
        "PATH": PATH_ENV_VAR,
    }
)

# See the CPython docs for more info:
# - General: https://devguide.python.org/setup/#compile-and-build
# - Static builds: https://wiki.python.org/moin/BuildStatically


def _run_cpython_cmd(label, cmd_array):
    cmd_str = " ".join(cmd_array)
    print("CPYTHON BUILD STEP: {}".format(label))
    print(cmd_str)

    run(cmd_str, shell=True, check=True, cwd=CPYTHON_SRC, env=ENV_VARS)


@task(default=True)
def build(ctx, clean=False, noconf=False, nobuild=False):
    """
    Build CPython to WebAssembly
    """
    if exists(join(CPYTHON_SRC, "Makefile")) and clean:
        _run_cpython_cmd("clean", ["make", "clean"])

    # These flags are relevant for building static extensions and CPython
    # itself
    cflags = [
        WASM_CFLAGS,
        "-m32", 
        "-DCONFIG_32",
        "-DANSI",
    ]

    ldflags = [
        "-static",
        "-Xlinker --no-gc-sections",
    ]

    # Shared compiler and liker arguments are used to build all C-extensions
    # in both the CPython and module builds. However, in the CPython build we
    # statically link all the C-extensions we need, therefore these are only
    # relevant in the module builds.
    #
    cc_shared = [
        WASM_CC,
        "-D__wasi__",
        "-nostdlib",
        "-nostdlib++",
        "-fPIC",
        "--target=wasm32-unknown-emscripten",
    ]

    ldshared = [
        WASM_CC,
        "-nostdlib",
        "-nostdlib++",
        "-Xlinker --no-entry",
        "-Xlinker --shared",
        "-Xlinker --export-all",
        "-Xlinker --no-gc-sections",
    ]

    # Link in extra wasi-libc long double support (see wasi-libc docs)
    link_libs = "-lc-printscan-long-double"

    # Configure
    configure_cmd = [
        "CONFIG_SITE=./config.site",
        "READELF=true",
        "./configure",
        'LIBS="{}"'.format(link_libs),
        "CC={}".format(WASM_CC),
        "CXX={}".format(WASM_CXX),
        "CPP={}".format(WASM_CPP),
        "AR={}".format(WASM_AR),
        "RANLIB={}".format(WASM_RANLIB),
        "LD={}".format(WASM_CC),
        'CFLAGS="{}"'.format(" ".join(cflags)),
        'CPPFLAGS="{}"'.format(" ".join(cflags)),
        'LDFLAGS="{}"'.format(" ".join(ldflags)),
        'CCSHARED="{}"'.format(" ".join(cc_shared)),
        'LDSHARED="{}"'.format(" ".join(ldshared)),
        "--disable-ipv6",
        "--disable-shared",
        "--build={}".format(WASM_BUILD),
        "--host={}".format(WASM_HOST),
        "--prefix={}".format(INSTALL_DIR),
    ]

    if not noconf:
        _run_cpython_cmd("configure", configure_cmd)

    if not nobuild:
        # Copy in extra undefs
        _run_cpython_cmd(
            "modify", ["cat", "pyconfig-extra.h", ">>", "pyconfig.h"]
        )

        # Note, the CPython static linking guide says to pass -static to
        # LDFLAGS here, but wasm-ld doesn't recognise this flag
        make_cmd = [
            "make -j {}".format(USABLE_CPUS),
        ]
        _run_cpython_cmd("make", make_cmd)
        _run_cpython_cmd("libpython", ["make", LIBPYTHON_NAME])

    # Run specific install tasks (see cpython/Makefile)
    _run_cpython_cmd("commoninstall", ["make", "commoninstall"])
    _run_cpython_cmd("bininstall", ["make", "bininstall"])
