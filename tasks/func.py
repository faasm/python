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
from tasks.env import CPYTHON_FUNC_USER, CPYTHON_FUNC_NAME, PROJ_ROOT

FAASM_SHARED_STORAGE_ROOT = join(FAASM_LOCAL_DIR, "shared")
PY_FUNC_DIR = join(PROJ_ROOT, "func", "python")
PY_UPLOAD_DIR = join(FAASM_SHARED_STORAGE_ROOT, "pyfuncs", "python")


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
    Invoke a python function on a Faasm cluster
    """
    host, port = get_faasm_invoke_host_port()
    url = "http://{}:{}".format(host, port)
    data = {
        "user": CPYTHON_FUNC_USER,
        "function": CPYTHON_FUNC_NAME,
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
