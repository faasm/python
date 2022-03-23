from faasmtools.compile_util import wasm_cmake
from faasmtools.env import WASM_DIR
from faasmtools.build import FAASM_LOCAL_DIR
from faasmtools.endpoints import (
    get_faasm_invoke_host_port,
    get_faasm_upload_host_port,
    get_knative_headers,
)

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
def upload(ctx):
    """
    Upload the CPython function
    """
    host, port = get_faasm_upload_host_port()
    url = "http://{}:{}/f/{}/{}".format(host, port, USER, FUNC)
    print("Uploading {}/{} to {}".format(USER, FUNC, url))
    response = requests.put(url, data=open(WASM_FILE, "rb"))

    print("Response ({}): {}".format(response.status_code, response.text))


@task
def uploadpy(ctx, func, local=False):
    """
    Upload the given Python function
    """
    host, port = get_faasm_upload_host_port()
    src_file = join(PY_FUNC_DIR, "{}.py".format(func))

    if local:
        makedirs(PY_UPLOAD_DIR, exist_ok=True)
        func_upload_dir = join(PY_UPLOAD_DIR, func)
        makedirs(func_upload_dir, exist_ok=True)

        dest_file = join(func_upload_dir, "function.py")
        print("Copying function {} {} -> {}".format(func, src_file, dest_file))
        copy(src_file, dest_file)
    else:
        url = "http://{}:{}/p/{}/{}".format(host, port, "python", func)
        response = requests.put(url, data=open(src_file, "rb"))

        print("Response ({}): {}".format(response.status_code, response.text))


@task
def upload_all(ctx, local=False):
    """
    Upload all Python functions
    """
    funcs = listdir(PY_FUNC_DIR)
    funcs = [f for f in funcs if f.endswith(".py")]
    funcs = [f.replace(".py", "") for f in funcs]

    for func in funcs:
        uploadpy(ctx, func, local=local)


@task
def invoke(ctx, user, func, input_data=None):
    """
    Invoke a function
    """
    host, port = get_faasm_invoke_host_port()
    url = "http://{}:{}".format(host, port)
    data = {
        "user": USER,
        "function": FUNC,
        "py_user": user,
        "py_func": func,
        "python": True,
    }

    if input_data:
        data["input_data"] = input_data

    headers = get_knative_headers()
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print("Error ({}):\n{}".format(response.status_code, response.text))
        exit(1)

    print("Success:\n{}".format(response.text))
