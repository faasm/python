import os

from copy import copy
from tasks.env import (
    CMAKE_TOOLCHAIN_FILE,
    CROSSENV_DIR,
    PROJ_ROOT,
    THIRD_PARTY_DIR,
    USABLE_CPUS,
    WASM_LIB_INSTALL,
)
from os.path import join
from subprocess import run
from invoke import task, Failure

MXNET_LIB = join(WASM_LIB_INSTALL, "libmxnet.so")

# Modified libs
MODIFIED_LIBS = {
    "pyfaasm": {
        "dir": join(PROJ_ROOT, "pyfaasm"),
    },
}

MODIFIED_LIBS_EXPERIMENTAL = {
    # 15/11/2022 - Move Numpy back to experimental as either the upgrades
    # to the CPP toolchain or LLVM 13 break the build
    "numpy": {
        "env": {"NPY_NUM_BUILD_JOBS": USABLE_CPUS},
    },
    "horovod": {
        "env": {
            "MAKEFLAGS": "-j{}".format(USABLE_CPUS),
            "HOROVOD_TOOLCHAIN_FILE": CMAKE_TOOLCHAIN_FILE,
            "HOROVOD_WITH_MXNET": "1",
            "HOROVOD_WITH_MPI": "1",
            "HOROVOD_WITH_TENSORFLOW": "0",
            "HOROVOD_WITH_PYTORCH": "0",
            "HOROVOD_WITHOUT_GLOO": "1",
        },
        "pip_cmd": "pip install .[mxnet]",
    },
    "mxnet": {
        "dir": join(THIRD_PARTY_DIR, "mxnet", "python"),
        "env": {"MXNET_LIBRARY_PATH": MXNET_LIB},
    },
}

MODIFIED_LIBS_ALL = copy(MODIFIED_LIBS)
MODIFIED_LIBS_ALL.update(MODIFIED_LIBS_EXPERIMENTAL)

# Libs that can be installed directly from PyPI
PYPI_LIBS = [
    "dulwich",
    "Genshi",
    "pyaes",
    "pyperf",
    "pyperformance",
    "six",
]


def _check_crossenv_on():
    actual = os.environ.get("VIRTUAL_ENV")
    if actual != CROSSENV_DIR:
        print(
            "Got VIRTUAL_ENV={} but expected {}".format(actual, CROSSENV_DIR)
        )
        raise Failure("Cross-env not activated")


@task
def show(ctx):
    """
    List supported libraries
    """
    print("We currently support the following libraries:")

    print("\n--- Direct from PyPI ---")
    for lib_name in PYPI_LIBS:
        print(lib_name)

    print("\n--- With modifications ---")
    for lib_name in MODIFIED_LIBS.keys():
        print(lib_name)

    print("\n--- Experimental ---")
    for lib_name in MODIFIED_LIBS_EXPERIMENTAL.keys():
        print(lib_name)

    print("")


@task
def build(ctx, name=None, experimental=False):
    """
    Install cross-compiled libraries
    """
    _check_crossenv_on()

    # Work out which modules to install
    modified_libs = dict()
    pypi_libs = list()

    if not name:
        if experimental:
            modified_libs = MODIFIED_LIBS_EXPERIMENTAL
        else:
            modified_libs = MODIFIED_LIBS
            pypi_libs = PYPI_LIBS
    elif name in MODIFIED_LIBS_ALL.keys():
        modified_libs = {name: MODIFIED_LIBS_ALL[name]}
    else:
        if name not in PYPI_LIBS:
            print("WARNING: {} not definitely supported!".format(name))

        pypi_libs = [name]

    # Install modified libs
    for lib_name, lib_def in modified_libs.items():

        shell_env = copy(os.environ)
        extra_env = lib_def.get("env", {})
        shell_env.update(extra_env)

        # Work out install directory
        mod_dir = lib_def.get("dir", join(THIRD_PARTY_DIR, lib_name))
        print("Installing modified lib {} from {}".format(lib_name, mod_dir))

        # Execute the pip command
        pip_cmd = lib_def.get("pip_cmd", "pip install .")
        print(pip_cmd)
        run(pip_cmd, cwd=mod_dir, shell=True, check=True, env=shell_env)

    # Install pypi libs
    for lib_name in pypi_libs:
        print("Installing lib from PyPI {}".format(lib_name))
        run("pip install {}".format(lib_name), shell=True, check=True)
