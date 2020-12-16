from subprocess import run
from os import environ
from copy import copy
from os.path import join


from tasks.env import (
    PROJ_ROOT,
    FAASM_NATIVE_INSTALL,
)

from invoke import task

PYFAASM_DIR = join(PROJ_ROOT, "pyfaasm")
NATIVE_LIBS = join(FAASM_NATIVE_INSTALL, "lib")
USR_LOCAL_LIBS = "/usr/local/lib"
LD_LIBRARY_PATH = "{}:{}".format(NATIVE_LIBS, USR_LOCAL_LIBS)


@task
def native(ctx):
    """
    Run native build of the pyfaasm library
    """
    print("Installing pyfaasm in development mode")
    run(
        "pip3 install -e .",
        shell=True,
        check=True,
        cwd=PYFAASM_DIR,
    )


@task
def test(ctx):
    """
    Run pyfaasm tests natively
    """
    shell_env = copy(environ)
    ld_path = shell_env.get("LD_LIBRARY_PATH")
    ld_path = (
        "{}:{}".format(LD_LIBRARY_PATH, ld_path)
        if ld_path
        else LD_LIBRARY_PATH
    )

    shell_env.update(
        {
            "PYTHON_LOCAL_CHAINING": "1",
            "LD_LIBRARY_PATH": LD_LIBRARY_PATH,
        }
    )

    run(
        "python3 -m unittest",
        shell=True,
        check=True,
        cwd=PYFAASM_DIR,
        env=shell_env,
    )
