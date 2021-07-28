from faasmtools.compile_util import wasm_cmake
from faasmtools.env import WASM_DIR
from faasmtools.build import FAASM_LOCAL_DIR

import requests
from os.path import join
from invoke import task
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

FAASM_SHARED_STORAGE_ROOT = join(FAASM_LOCAL_DIR, "shared")
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
def upload(ctx, host="upload", port=8002):
    url = "http://{}:{}/f/{}/{}".format(host, port, USER, FUNC)
    response = requests.put(url, data=open(WASM_FILE, "rb"))

    print("Response {}: {}".format(response.status_code, response.text))


@task
def uploadpy(ctx, local=False, host="upload", port=8002):
    """
    Upload functions written in Python
    """
    # Get all Python funcs
    funcs = listdir(PY_FUNC_DIR)
    funcs = [f for f in funcs if f.endswith(".py")]
    funcs = [f.replace(".py", "") for f in funcs]

    for func in funcs:
        src_file = join(PY_FUNC_DIR, "{}.py".format(func))

        if local:
            makedirs(PY_UPLOAD_DIR, exist_ok=True)
            func_upload_dir = join(PY_UPLOAD_DIR, func)
            makedirs(func_upload_dir, exist_ok=True)

            dest_file = join(func_upload_dir, "function.py")

            copy(src_file, dest_file)
        else:
            url = "http://{}:{}/p/{}/{}".format(host, port, "python", func)
            response = requests.put(url, data=open(src_file, "rb"))

            print(
                "{} response {}: {}".format(
                    func, response.status_code, response.text
                )
            )
