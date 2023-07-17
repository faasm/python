from base64 import b64encode
from faasmctl.util.invoke import invoke_wasm
from faasmctl.util.upload import upload_python
from faasmtools.build import FAASM_LOCAL_DIR
from invoke import task
from os import makedirs, listdir
from os.path import join
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
    src_file = join(PY_FUNC_DIR, "{}.py".format(func))

    if local:
        makedirs(PY_UPLOAD_DIR, exist_ok=True)
        func_upload_dir = join(PY_UPLOAD_DIR, func)
        makedirs(func_upload_dir, exist_ok=True)

        dest_file = join(func_upload_dir, "function.py")
        print("Copying function {} {} -> {}".format(func, src_file, dest_file))
        copy(src_file, dest_file)
    else:
        upload_python(func, src_file)


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
    data = {
        "user": CPYTHON_FUNC_USER,
        "function": CPYTHON_FUNC_NAME,
        "py_user": user,
        "py_func": func,
        "python": True,
    }

    if input_data:
        data["input_data"] = b64encode(input_data.encode("utf-8")).decode(
            "utf-8"
        )

    # Invoke message
    response = invoke_wasm(data)

    print("Success:\n{}".format(response.messageResults[0].outputData))
