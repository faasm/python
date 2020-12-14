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


@task
def native(ctx):
    """
    Run native build of the pyfaasm library
    """
    run(
        "pip3 install .",
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
    shell_env.update(
        {
            "PYTHON_LOCAL_CHAINING": "1",
        }
    )

    run(
        "python3 -m unittest",
        shell=True,
        check=True,
        cwd=PYFAASM_DIR,
        env=shell_env,
    )
