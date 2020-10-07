import logging
from os.path import join, abspath, dirname, exists
from shutil import rmtree

from crossenv import CrossEnvBuilder

PROJ_ROOT = dirname(dirname(abspath(__file__)))

WASM_CPYTHON = join(
    PROJ_ROOT, "third-party", "cpython", "install", "wasm", "bin", "python3.8"
)

CROSSENV_VENV_DIR = join(PROJ_ROOT, "cross_venv")
CROSSENV_SYSROOT = "/usr/local/faasm/llvm-sysroot"


def main():
    # Clean existing crossenv virtual environment
    if exists(CROSSENV_VENV_DIR):
        print("Removing existing crossenv at {}".format(CROSSENV_VENV_DIR))
        rmtree(CROSSENV_VENV_DIR)

    # Set logging level
    level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Invoke the cross-env builder
    print("Building crossenv at {}".format(CROSSENV_VENV_DIR))
    builder = CrossEnvBuilder(
        with_cross_pip=True,
        with_build_pip=True,
        host_python=WASM_CPYTHON,
        host_sysroot=CROSSENV_SYSROOT,
    )
    builder.create(CROSSENV_VENV_DIR)


if __name__ == "__main__":
    main()
