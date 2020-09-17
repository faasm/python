import os

from copy import copy
from multiprocessing import cpu_count
from os.path import join, exists, dirname, realpath
from subprocess import run
from os import makedirs
from shutil import copyfile, copytree, rmtree

from faasmcli.util.files import clean_dir
from faasmcli.util.toolchain import (
    BASE_CONFIG_CMD,
    WASM_CC,
    WASM_CPP,
    WASM_AR,
    WASM_CXX,
    WASM_RANLIB,
    WASM_BUILD,
    WASM_LDSHARED,
    WASM_CFLAGS,
    WASM_HOST,
    WASM_SYSROOT,
    WASM_LIB_INSTALL,
)
from faasmcli.util.env import FAASM_RUNTIME_ROOT

from invoke import task

THIS_DIR = dirname(realpath(__file__))

# The python library name might have a letter at the end of it,
# e.g. for a debug build it'll be libpython3.8d.a and with
# pymalloc it'll be libpython3.8m.a
LIBPYTHON_NAME = "libpython3.8.a"

# We need to have a version of Python installed on the host with _exactly_
# the same version as the one we're building
BUILD_PYTHON_BIN = "/usr/local/faasm/python3.8/bin"
BUILD_PYTHON_EXE = join(BUILD_PYTHON_BIN, "python3.8")
BUILD_PYTHON_PIP = join(BUILD_PYTHON_BIN, "pip3.8")

CROSSENV_DIR = join(THIS_DIR, "cross_venv")

CPYTHON_SRC = join(THIS_DIR, "third-party", "cpython")
WORK_DIR = join(CPYTHON_SRC)
BUILD_DIR = join(WORK_DIR, "build", "wasm")

INSTALL_DIR = join(WORK_DIR, "install", "wasm")
WASM_PYTHON = join(INSTALL_DIR, "bin", "python3.8")

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


def _run_cmd(label, cmd_array):
    cmd_str = " ".join(cmd_array)
    print("CPYTHON BUILD STEP: {}".format(label))
    print(cmd_str)
    res = run(cmd_str, shell=True, cwd=WORK_DIR, env=ENV_VARS)

    if res.returncode != 0:
        raise RuntimeError(
            "CPython {} failed ({})".format(label, res.returncode)
        )


@task
def cpython(ctx, clean=False, noconf=False, nobuild=False):
    """
    Build CPython to WebAssembly
    """

    clean_dir(BUILD_DIR, clean)
    clean_dir(INSTALL_DIR, clean)
    if clean:
        _run_cmd("clean", ["make", "clean"])

    # Configure
    configure_cmd = [
        "CONFIG_SITE=./config.site",
        "READELF=true",
        "./configure",
    ]

    configure_cmd.extend([
        "CC={}".format(WASM_CC),
        "CXX={}".format(WASM_CXX),
        "CPP={}".format(WASM_CPP),
        "AR={}".format(WASM_AR),
        "RANLIB={}".format(WASM_RANLIB),
        "LD={}".format(WASM_CC),
    ])

    configure_cmd.extend(
        [
            "--disable-ipv6",
            "--disable-shared",
            "--build={}".format(WASM_BUILD),
            "--host={}".format(WASM_HOST),
            "--prefix={}".format(INSTALL_DIR),
        ]
    )

    cflags = [
        WASM_CFLAGS,
    ]
    cflags = " ".join(cflags)

    ldflags = [
            "-static",
#            "-Xlinker --export-all",
            "-Xlinker --no-gc-sections",
            ]
    ldflags = " ".join(ldflags)

    # Arguments to wasm-ld for building C extensions
    # Used for both CPython builtins and other modules
    ldshared = [
            WASM_CC,
            "-Xlinker --no-entry",
#            "-Xlinker --export-all",
            "-Xlinker --no-gc-sections",
            "-L {}".format(WASM_LIB_INSTALL),
            ]
    ldshared = " ".join(ldshared)

    configure_cmd.extend(
        [
            'CFLAGS="{}"'.format(cflags),
            'CPPFLAGS="{}"'.format(cflags),
            'LDFLAGS="{}"'.format(ldflags),
            'EXT_SUFFIX=.so',
            'SHLIB_SUFFIX=.so',
            'LDSHARED="{}"'.format(ldshared),
            'LDCXXSHARED="{}"'.format(ldshared),
        ]
    )

    if not noconf:
        _run_cmd("configure", configure_cmd)

    if not nobuild:
        # Copy in extra undefs
        _run_cmd("modify", ["cat", "pyconfig-extra.h", ">>", "pyconfig.h"])

        cpus = int(cpu_count()) - 1

        # Note, the CPython static linking guide says to pass -static to 
        # LDFLAGS here, but wasm-ld doesn't recognise this flag
        make_cmd = [
            "make -j {}".format(cpus),
            'LDFLAGS="-static"',
            'LINKFORSHARED=" "',
        ]
        _run_cmd("make", make_cmd)
        _run_cmd("libpython", ["make", LIBPYTHON_NAME])

    # Run specific install tasks (see cpython/Makefile)
    _run_cmd("commoninstall", ["make", "commoninstall"])
    _run_cmd("bininstall", ["make", "bininstall"])

    # Copy library file into place
    copyfile(
        join(WORK_DIR, LIBPYTHON_NAME),
        join(INSTALL_DIR, "lib", LIBPYTHON_NAME),
    )


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


@task
def crossenv(ctx, clean=False):
    """
    Sets up the cross-compile environment
    """

    if exists(CROSSENV_DIR) and clean:
        rmtree(CROSSENV_DIR)

    if exists(CROSSENV_DIR):
        print("Crossenv already set up, skipping install")
    else:
        # Install crossenv in our build python
        run(
            "{} install crossenv".format(BUILD_PYTHON_PIP),
            shell=True,
            check=True,
            cwd=THIS_DIR,
            env=ENV_VARS,
        )

        # See the crossenv commandline args:
        # https://github.com/benfogle/crossenv/blob/master/crossenv/__init__.py
        crossenv_setup = [
            BUILD_PYTHON_EXE,
            "-m crossenv",
            WASM_PYTHON,
            "cross_venv",
            "--sysroot={}".format(WASM_SYSROOT),
        ]
        
        crossenv_cmd = " ".join(crossenv_setup)
        print(crossenv_cmd)

        run(
            crossenv_cmd,
            shell=True,
            check=True,
            cwd=THIS_DIR,
            env=ENV_VARS,
        )

