import glob

from os.path import join, exists
from shutil import rmtree, copytree
from subprocess import run
from os import makedirs, remove

from invoke import task

from faasmtools.build import FAASM_LOCAL_DIR

from tasks.env import PROJ_ROOT, THIRD_PARTY_DIR

FAASM_RUNTIME_ROOT = join(FAASM_LOCAL_DIR, "runtime_root")
CPYTHON_SRC = join(THIRD_PARTY_DIR, "cpython")
CPYTHON_INSTALL_DIR = join(CPYTHON_SRC, "install", "wasm")
CROSSENV_WASM_DIR = join(PROJ_ROOT, "cross_venv", "cross")

INCLUDE_ROOT = join(FAASM_RUNTIME_ROOT, "include")
LIB_ROOT = join(FAASM_RUNTIME_ROOT, "lib")

INCLUDE_SRC_DIR = join(CPYTHON_INSTALL_DIR, "include", "python3.8")
LIB_SRC_DIR = join(CPYTHON_INSTALL_DIR, "lib", "python3.8")
SITE_PACKAGES_SRC_DIR = join(
    CROSSENV_WASM_DIR, "lib", "python3.8", "site-packages"
)

INCLUDE_DEST_DIR = join(INCLUDE_ROOT, "python3.8")
LIB_DEST_DIR = join(LIB_ROOT, "python3.8")
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


@task
def cpython(ctx):
    # Remove dirs to be replaced by those we copy in
    if exists(INCLUDE_DEST_DIR):
        print("Removing {}".format(INCLUDE_DEST_DIR))
        rmtree(INCLUDE_DEST_DIR)

    if exists(LIB_DEST_DIR):
        print("Removing {}".format(LIB_DEST_DIR))
        rmtree(LIB_DEST_DIR)

    # Copy CPython includes
    print("Copying {} to {}".format(INCLUDE_SRC_DIR, INCLUDE_DEST_DIR))
    copytree(INCLUDE_SRC_DIR, INCLUDE_DEST_DIR)

    # Copy CPython libs
    print("Copying {} to {}".format(LIB_SRC_DIR, LIB_DEST_DIR))
    copytree(LIB_SRC_DIR, LIB_DEST_DIR)


@task(default=True)
def copy(ctx):
    """
    Copies the CPython archive and all installed modules from the cpython build
    into the Faasm runtime root
    """
    if not exists(LIB_ROOT):
        print("Creating {}".format(LIB_ROOT))
        makedirs(LIB_ROOT)

    if not exists(INCLUDE_ROOT):
        print("Creating {}".format(INCLUDE_ROOT))
        makedirs(INCLUDE_ROOT)

    # Clear out pyc files
    print("Clearing out pyc files")
    _clear_pyc_files(LIB_SRC_DIR)
    _clear_pyc_files(SITE_PACKAGES_SRC_DIR)

    # Copy CPython
    cpython()

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
