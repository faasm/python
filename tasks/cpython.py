import os
from copy import copy
from multiprocessing import cpu_count
from os.path import join, exists
from subprocess import run
from os import makedirs
from shutil import copyfile, copytree, rmtree

from faasmcli.util.compile import wasm_cmake, wasm_copy_upload
from faasmcli.util.files import clean_dir
from faasmcli.util.toolchain import (
    BASE_CONFIG_CMD,
    WASM_BUILD,
    WASM_CFLAGS,
    WASM_HOST,
    WASM_LDFLAGS,
)
from faasmcli.util.env import (
    FAASM_RUNTIME_ROOT
        )

from invoke import task

from tasks.util.env import (
    EXPERIMENTS_FUNC_BUILD_DIR,
    EXPERIMENTS_FUNC_DIR,
    EXPERIMENTS_THIRD_PARTY,
)

# The python library name might have a letter at the end of it,
# e.g. for a debug build it'll be libpython3.8d.a and with
# pymalloc it'll be libpython3.8m.a
LIBPYTHON_NAME = "libpython3.8.a"

CPYTHON_DIR = join(EXPERIMENTS_THIRD_PARTY, "cpython")
LOCAL_PYTHON_BIN = "/usr/local/faasm/python3.8/bin"
WORK_DIR = join(CPYTHON_DIR)
BUILD_DIR = join(WORK_DIR, "build", "wasm")
INSTALL_DIR = join(WORK_DIR, "install", "wasm")

# Environment variables
ENV_VARS = copy(os.environ)
PATH_ENV_VAR = ENV_VARS.get("PATH", "")
PATH_ENV_VAR = "{}:{}".format(LOCAL_PYTHON_BIN, PATH_ENV_VAR)
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
def lib(ctx, clean=False, noconf=False, nobuild=False):
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

    configure_cmd.extend(BASE_CONFIG_CMD)
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
        WASM_LDFLAGS,
        "-static",
    ]
    ldflags = " ".join(ldflags)

    configure_cmd.extend(
        [
            'CFLAGS="{}"'.format(cflags),
            'CPPFLAGS="{}"'.format(cflags),
            'LDFLAGS="{}"'.format(ldflags),
        ]
    )

    if not noconf:
        _run_cmd("configure", configure_cmd)

    if not nobuild:
        # Copy in extra undefs
        _run_cmd("modify", ["cat", "pyconfig-extra.h", ">>", "pyconfig.h"])

        cpus = int(cpu_count()) - 1
        make_cmd = [
            "make -j {}".format(cpus),
            'LDFLAGS="-static"',
            'LINKFORSHARED=" "',
        ]
        _run_cmd("make", make_cmd)
        _run_cmd("libpython", ["make", LIBPYTHON_NAME])

    _run_cmd("inclinstall", ["make", "inclinstall"])
    _run_cmd("libinstall", ["make", "libinstall"])

    # Copy library file into place
    copyfile(
            join(WORK_DIR, LIBPYTHON_NAME),
            join(INSTALL_DIR, "lib", LIBPYTHON_NAME)
            )


@task
def func(ctx, clean=False):
    wasm_cmake(
        EXPERIMENTS_FUNC_DIR, EXPERIMENTS_FUNC_BUILD_DIR, "mini", clean=clean
    )

    wasm_file = join(EXPERIMENTS_FUNC_BUILD_DIR, "cpy", "mini.wasm")
    wasm_copy_upload("cpy", "mini", wasm_file)


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

