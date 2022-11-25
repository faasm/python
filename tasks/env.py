from multiprocessing import cpu_count
from os.path import join, dirname, realpath
from faasmtools.build import FAASM_LOCAL_DIR

PROJ_ROOT = dirname(dirname(realpath(__file__)))
THIRD_PARTY_DIR = join(PROJ_ROOT, "third-party")
CROSSENV_DIR = join(PROJ_ROOT, "cross_venv", "cross")

FAASM_RUNTIME_ROOT = join(FAASM_LOCAL_DIR, "runtime_root")
USABLE_CPUS = str(int(cpu_count()) - 1)
VERSION_FILE = join(PROJ_ROOT, "VERSION")
FAASM_NATIVE_INSTALL = "/usr/local/faasm/native"

PYTHON_VERSION = "Python-3.8.2"
PYTHON_INSTALL_DIR = join(FAASM_LOCAL_DIR, "python3.8")

CPYTHON_FUNC_USER = "python"
CPYTHON_FUNC_NAME = "py_func"


def get_version():
    with open(VERSION_FILE) as fh:
        version = fh.read().strip()

    return version
