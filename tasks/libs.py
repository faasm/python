import os

from copy import copy
from multiprocessing import cpu_count
from os.path import join, dirname, realpath
from subprocess import run


from invoke import task, Failure

USABLE_CPUS = str(int(cpu_count()) - 1)

PROJ_ROOT = dirname(realpath(__file__))
THIRD_PARTY_DIR = join(PROJ_ROOT, "third-party")
CROSSENV_DIR = join(PROJ_ROOT, "cross_venv", "cross")

# Modified libs
MODIFIED_LIBS = {
    "numpy": {
        "env": {"NPY_NUM_BUILD_JOBS": USABLE_CPUS},
    },
    "horovod": {
        "env": {"HOROVOD_WITH_MXNET": "1"},
    },
    "mxnet": {"subdir": "python"},
}

# Libs that can be installed with no modifications
UNMODIFIED_LIBS = [
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
def list(ctx):
    """
    List supported libraries
    """
    print("We currently support the following libraries:")

    print("\n--- Unmodified ---")
    for lib in UNMODIFIED_LIBS:
        print(lib)

    print("\n--- With modifications ---")
    for lib in MODIFIED_LIBS:
        print(lib)

    print("")


@task
def install(ctx, lib):
    """
    Install cross-compiled libraries
    """
    _check_crossenv_on()

    modified = list()
    unmodified = list()

    if lib == "all":
        modified = MODIFIED_LIBS.keys()
        unmodified = UNMODIFIED_LIBS
    elif lib in MODIFIED_LIBS.keys():
        modified = [lib]
    elif lib in UNMODIFIED_LIBS:
        unmodified = [lib]
    else:
        print("WARNING: module not recognised, may not work!")
        unmodified = [lib]

    for lib in modified:
        print("Installing modified lib {}".format(lib))
        lib_def = MODIFIED_LIBS[lib]

        shell_env = copy(os.environ)
        if "env" in lib_def:
            shell_env.update(lib_def["env"])

        mod_dir = join(THIRD_PARTY_DIR, lib)
        if "subdir" in lib_def:
            mod_dir = join(mod_dir, lib_def["subdir"])

        run(
            "pip install .", cwd=mod_dir, shell=True, check=True, env=shell_env
        )

    for lib in unmodified:
        print("Installing unmodified lib {}".format(lib))
        run("pip install {}".format(lib), shell=True, check=True)
