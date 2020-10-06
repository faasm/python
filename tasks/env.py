from multiprocessing import cpu_count
from os.path import join, dirname, realpath

PROJ_ROOT = dirname(dirname(realpath(__file__)))

THIRD_PARTY_DIR = join(PROJ_ROOT, "third-party")
CROSSENV_DIR = join(PROJ_ROOT, "cross_venv", "cross")

FAASM_SYSROOT = "/usr/local/faasm/llvm-sysroot"
FAASM_TOOLCHAIN_FILE = (
    "/usr/local/code/faasm/third-party/faasm-toolchain/WasiToolchain.cmake"
)

USABLE_CPUS = str(int(cpu_count()) - 1)
