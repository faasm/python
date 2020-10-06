import os

from copy import copy
from os.path import join
from subprocess import run
from tasks.env import USABLE_CPUS, THIRD_PARTY_DIR, CROSSENV_DIR

from invoke import task, Failure

# Modified libs
MODIFIED_LIBS = {
    "numpy": {
        "env": {"NPY_NUM_BUILD_JOBS": USABLE_CPUS},
    },
    "horovod": {
        "env": {"HOROVOD_WITH_MXNET": "1"},
        "experimental": True,
    },
    "mxnet": {
        "subdir": "python",
        "experimental": True,
    },
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
def show(ctx):
    """
    List supported libraries
    """
    print("We currently support the following libraries:")

    print("\n--- Unmodified ---")
    for lib_name in UNMODIFIED_LIBS:
        print(lib_name)

    print("\n--- With modifications ---")
    for lib_name, lib_def in MODIFIED_LIBS.items():
        experimental = lib_def.get("experimental", False)
        output = (
            "{} (experimental)".format(lib_name) if experimental else lib_name
        )
        print(output)

    print("")


@task
def install(ctx, lib_name):
    """
    Install cross-compiled libraries
    """
    _check_crossenv_on()

    modified = dict()
    unmodified = list()

    if lib_name == "all":
        # All except experimental
        modified = [
            lib_name
            for lib_name, lib_def in MODIFIED_LIBS.items()
            if not lib_def.get("experimental")
        ]
        unmodified = UNMODIFIED_LIBS
    elif lib_name == "all-experimental":
        modified = MODIFIED_LIBS.keys()
        unmodified = UNMODIFIED_LIBS
    elif lib_name in MODIFIED_LIBS.keys():
        modified = {lib_name: dict()}
    elif lib_name in UNMODIFIED_LIBS:
        unmodified = [lib_name]
    else:
        print("WARNING: module not recognised, may not work!")
        unmodified = [lib_name]

    for lib_name, lib_def in modified.items():
        print("Installing modified lib {}".format(lib_name))

        shell_env = copy(os.environ)
        if "env" in lib_def:
            shell_env.update(lib_def["env"])

        mod_dir = join(THIRD_PARTY_DIR, lib_name)
        if "subdir" in lib_def:
            mod_dir = join(mod_dir, lib_def["subdir"])

        run(
            "pip install .", cwd=mod_dir, shell=True, check=True, env=shell_env
        )

    for lib_name in unmodified:
        print("Installing unmodified lib {}".format(lib_name))
        run("pip install {}".format(lib_name), shell=True, check=True)
