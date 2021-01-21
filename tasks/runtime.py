import glob

from os.path import join, exists
from shutil import rmtree
from subprocess import run
from os import makedirs, remove

from invoke import task

from tasks.env import PROJ_ROOT, THIRD_PARTY_DIR, FAASM_RUNTIME_ROOT

CPYTHON_SRC = join(THIRD_PARTY_DIR, "cpython")
CPYTHON_INSTALL_DIR = join(CPYTHON_SRC, "install", "wasm")
CROSSENV_WASM_DIR = join(PROJ_ROOT, "cross_venv", "cross")

LIB_SRC_DIR = join(CPYTHON_INSTALL_DIR, "lib", "python3.8")
LIB_DEST_DIR = join(FAASM_RUNTIME_ROOT, "lib", "python3.8")

SITE_PACKAGES_SRC_DIR = join(
    CROSSENV_WASM_DIR, "lib", "python3.8", "site-packages"
)
SITE_PACKAGES_DEST_DIR = join(LIB_DEST_DIR, "site-packages")


def _glob_remove(glob_pattern, recursive=False, directory=False):
    print("Recursive remove: {}".format(glob_pattern))
    for filename in glob.iglob(glob_pattern, recursive=recursive):
        print("Removing {}".format(filename))
        if directory:
            rmtree(filename)
        else:
            remove(filename)


def _clear_pyc_files(dir_path):
    pyc_glob = "{}/**/*.pyc".format(dir_path)
    _glob_remove(pyc_glob, recursive=True)

    pycache_glob = "{}/**/__pycache__".format(dir_path)
    _glob_remove(pycache_glob, recursive=True, directory=True)


@task(default=True)
def copy(ctx):
    """
    Copies the installed modules into the Faasm runtime root
    """
    # Clear out pyc files
    print("Clearing out pyc files")
    _clear_pyc_files(LIB_SRC_DIR)
    _clear_pyc_files(SITE_PACKAGES_SRC_DIR)

    # Copy cross-compiled modules
    if not exists(SITE_PACKAGES_DEST_DIR):
        makedirs(SITE_PACKAGES_DEST_DIR)

    print(
        "Copying {} to {}".format(
            SITE_PACKAGES_SRC_DIR, SITE_PACKAGES_DEST_DIR
        )
    )
    run(
        "cp -r {}/* {}/".format(SITE_PACKAGES_SRC_DIR, SITE_PACKAGES_DEST_DIR),
        shell=True,
        check=True,
    )
