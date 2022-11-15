from multiprocessing import cpu_count
from os.path import dirname, join, realpath

PROJ_ROOT = dirname(dirname(dirname(realpath(__file__))))

THIRD_PARTY_DIR = join(PROJ_ROOT, "third-party")
CROSSENV_DIR = join(PROJ_ROOT, "cross_venv", "cross")
USABLE_CPUS = str(int(cpu_count()) - 1)

# WARNING: we copy this variables from `faasmtools/build.py` to avoid
# installing `faasmtools` in the cross-venv. Eventually we may have to find
# a way to import the variables from there
FAASM_LOCAL_DIR = "/usr/local/faasm"
CMAKE_TOOLCHAIN_FILE = join(FAASM_LOCAL_DIR, "tools", "WasiToolchain.cmake")
WASM_LIB_INSTALL = join(FAASM_LOCAL_DIR, "llvm-sysroot", "lib", "wasm32-wasi")
