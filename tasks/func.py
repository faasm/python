from faasmtools.compile_util import wasm_cmake
from faasmtools.env import WASM_DIR
from os.path import join
from invoke import task
from faasmtools.build import FAASM_LOCAL_DIR
from os import makedirs, listdir
from shutil import copy
from tasks.env import PROJ_ROOT

FUNC_DIR = join(PROJ_ROOT, "func", "cpp")
FUNC_BUILD_DIR = join(PROJ_ROOT, "build", "func")

USER = "python"
FUNC = "py_func"

WASM_FILE = join(FUNC_BUILD_DIR, "py_func.wasm")
DEST_FOLDER = join(WASM_DIR, USER, FUNC)
DEST_FILE = join(DEST_FOLDER, "function.wasm")

FAASM_SHARED_STORAGE_ROOT = join(FAASM_LOCAL_DIR, "shared_store")
PY_FUNC_DIR = join(PROJ_ROOT, "func", "python")
PY_UPLOAD_DIR = join(FAASM_SHARED_STORAGE_ROOT, "pyfuncs", "python")


@task(default=True, name="compile")
def compile(ctx, clean=False, debug=False):
    """
    Compile the CPython function
    """
    # Build the wasm
    wasm_cmake(FUNC_DIR, FUNC_BUILD_DIR, FUNC, clean, debug)

    # Copy the wasm into place

    makedirs(DEST_FOLDER, exist_ok=True)
    copy(WASM_FILE, DEST_FILE)


@task
def uploadpy(ctx, local=False):
    """
    Upload functions written in Python
    """
    if not local:
        raise RuntimeError("Remote upload not yet implemented")

    makedirs(PY_UPLOAD_DIR, exist_ok=True)

    # Get all Python funcs
    funcs = listdir(PY_FUNC_DIR)
    funcs = [f for f in funcs if f.endswith(".py")]
    funcs = [f.replace(".py", "") for f in funcs]

    for func in funcs:
        func_upload_dir = join(PY_UPLOAD_DIR, func)
        makedirs(func_upload_dir, exist_ok=True)

        src_file = join(PY_FUNC_DIR, "{}.py".format(func))
        dest_file = join(func_upload_dir, "function.py")
        copy(src_file, dest_file)
