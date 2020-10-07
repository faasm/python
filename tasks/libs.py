import os

from copy import copy
from os.path import join
from subprocess import run
from tasks.env import USABLE_CPUS, THIRD_PARTY_DIR, CROSSENV_DIR
from invoke import task, Failure

MXNET_LIB = "/usr/local/faasm/llvm-sysroot/lib/wasm32-wasi/libmxnet.so"


# Modified libs
MODIFIED_LIBS = {
    "numpy": {
        "env": {"NPY_NUM_BUILD_JOBS": USABLE_CPUS},
    },
}

MODIFIED_LIBS_EXPERIMENTAL = {
    "horovod": {
        "env": {"HOROVOD_WITH_MXNET": "1"},
    },
    "mxnet": {
        "subdir": "python",
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
def install(ctx, name=None, experimental=False):
    """
    Install cross-compiled libraries
    """
    _check_crossenv_on()

    # Work out which modules to install
    modified_libs = dict()
    pypi_libs = list()

    if name == "all":
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
        print("Installing modified lib {}".format(lib_name))

        shell_env = copy(os.environ)
        if "env" in lib_def:
            shell_env.update(lib_def["env"])

        mod_dir = join(THIRD_PARTY_DIR, lib_name)
        subdir = lib_def.get("subdir")
        if subdir:
            mod_dir = join(mod_dir, subdir)
            print("Installing from subdir: {}".format(mod_dir))

        run(
            "pip install .", cwd=mod_dir, shell=True, check=True, env=shell_env
        )

    # Install pypi libs
    for lib_name in pypi_libs:
        print("Installing lib from PyPI {}".format(lib_name))
        run("pip install {}".format(lib_name), shell=True, check=True)
