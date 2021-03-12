import os

from copy import copy
from faasmtools.build import WASM_LIB_INSTALL, CMAKE_TOOLCHAIN_FILE
from os.path import join
from subprocess import run
from invoke import task


@task(default=True)
def compile():
    pass


@task
def upload():
    pass
