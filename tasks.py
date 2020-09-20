import os

from copy import copy
from multiprocessing import cpu_count
from os.path import join, exists, dirname, realpath
from subprocess import run
from os import makedirs
from shutil import copytree, rmtree

from faasmcli.util.toolchain import (
    WASM_CC,
    WASM_CPP,
    WASM_AR,
    WASM_CXX,
    WASM_RANLIB,
    WASM_BUILD,
    WASM_CFLAGS,
    WASM_HOST,
    WASM_SYSROOT,
    WASM_LIB_INSTALL,
)
from faasmcli.util.env import FAASM_RUNTIME_ROOT

from invoke import task

PROJ_ROOT = dirname(realpath(__file__))

# The python library name might have a letter at the end of it,
# e.g. for a debug build it'll be libpython3.8d.a and with
# pymalloc it'll be libpython3.8m.a
LIBPYTHON_NAME = "libpython3.8.a"

# We need to have a version of Python installed on the host with _exactly_
# the same version as the one we're building
BUILD_PYTHON_BIN = "/usr/local/faasm/python3.8/bin"
BUILD_PYTHON_EXE = join(BUILD_PYTHON_BIN, "python3.8")
BUILD_PYTHON_PIP = join(BUILD_PYTHON_BIN, "pip3.8")

CROSSENV_DIR = join(PROJ_ROOT, "cross_venv")

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


@task
def cpython(ctx, clean=False, noconf=False, nobuild=False):
    """
    Build CPython to WebAssembly
    """
    if exists(join(CPYTHON_SRC, "Makefile")) and clean:
        _run_cpython_cmd("clean", ["make", "clean"])

    # These flags are relevant for building static extensions and CPython 
    # itself
    cflags = [
        WASM_CFLAGS,
    ]

    ldflags = [            
        "-static",
        "-Xlinker --no-gc-sections",
    ]

    # Shared compiler and liker arguments are used to build all C-extensions
    # in both the CPython and module builds. However, in the CPython build we 
    # statically link all the C-extensions we need, therefore these are only 
    # relevant in the module builds.
    cc_shared = [
        WASM_CC,
        "-nostdlib", "-nostdlib++", 
        "-fPIC",
        "--target=wasm32-unknown-emscripten",
    ]

    ldshared = [
        WASM_CC,
        "-nostdlib", "-nostdlib++",
        "-Xlinker --no-entry",
        "-Xlinker --shared",
        "-Xlinker --export-all",
        "-Xlinker --no-gc-sections",
        "-L {}".format(WASM_LIB_INSTALL),
    ]

    # Configure
    configure_cmd = [
        "CONFIG_SITE=./config.site",
        "READELF=true",
        "./configure",
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
        _run_cpython_cmd("modify", ["cat", "pyconfig-extra.h", ">>", "pyconfig.h"])

        cpus = int(cpu_count()) - 1

        # Note, the CPython static linking guide says to pass -static to 
        # LDFLAGS here, but wasm-ld doesn't recognise this flag
        make_cmd = [
            "make -j {}".format(cpus),
        ]
        _run_cpython_cmd("make", make_cmd)
        _run_cpython_cmd("libpython", ["make", LIBPYTHON_NAME])

    # Run specific install tasks (see cpython/Makefile)
    _run_cpython_cmd("commoninstall", ["make", "commoninstall"])
    _run_cpython_cmd("bininstall", ["make", "bininstall"])


@task
def runtime(ctx):
    include_root = join(FAASM_RUNTIME_ROOT, "include")
    lib_root = join(FAASM_RUNTIME_ROOT, "lib")
    if not exists(lib_root):
        makedirs(lib_root)

    if not exists(include_root):
        makedirs(include_root)

    include_src_dir = join(INSTALL_DIR, "include", "python3.8")
    lib_src_dir = join(INSTALL_DIR, "lib", "python3.8")

    include_dest_dir = join(include_root, "python3.8")
    lib_dest_dir = join(lib_root, "python3.8")

    if exists(include_dest_dir):
        rmtree(include_dest_dir)
        rmtree(lib_dest_dir)

    copytree(include_src_dir, include_dest_dir)
    copytree(lib_src_dir, lib_dest_dir)

