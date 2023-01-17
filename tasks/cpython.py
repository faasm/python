from copy import copy as deep_copy
from faasmtools.build import (
    FAASM_BUILD_ENV_DICT,
    WASM_HEADER_INSTALL,
    WASM_LIB_INSTALL,
    build_config_cmd,
)
from faasmtools.compile_util import wasm_cmake, wasm_copy_upload
from faasmtools.endpoints import get_faasm_upload_host_port
from faasmtools.env import WASM_DIR
from invoke import task
from os import environ, makedirs
from os.path import join, exists
from re import compile
from requests import put
from shutil import copy, copytree, rmtree
from subprocess import run
from tasks.env import (
    CPYTHON_FUNC_NAME,
    CPYTHON_FUNC_USER,
    FAASM_RUNTIME_ROOT,
    PROJ_ROOT,
    PYTHON_INSTALL_DIR,
    PYTHON_VERSION,
    USABLE_CPUS,
)

# The python library name might have a letter at the end of it,
# e.g. for a debug build it'll be libpython3.8d.a and with
# pymalloc it'll be libpython3.8m.a
LIBPYTHON_NAME = "libpython3.8.a"

# We need to have a version of Python installed on the host with _exactly_
# the same version as the one we're building
BUILD_PYTHON_BIN = "/usr/local/faasm/python3.8/bin"
BUILD_PYTHON_EXE = join(BUILD_PYTHON_BIN, "python3.8")
BUILD_PYTHON_PIP = join(BUILD_PYTHON_BIN, "pip3.8")

# CPython src
CPYTHON_SRC = join(PROJ_ROOT, "third-party", "cpython")
CPYTHON_BUILD_DIR = join(CPYTHON_SRC, "build", "wasm")

# CPython install
CPYTHON_INSTALL_DIR = join(CPYTHON_SRC, "install", "wasm")
WASM_PYTHON = join(CPYTHON_INSTALL_DIR, "bin", "python3.8")
WASM_PYTHON_INCLUDES = join(CPYTHON_INSTALL_DIR, "include")

# Environment variables
ENV_VARS = deep_copy(environ)
PATH_ENV_VAR = ENV_VARS.get("PATH", "")
PATH_ENV_VAR = "{}:{}".format(BUILD_PYTHON_BIN, PATH_ENV_VAR)
ENV_VARS.update(
    {
        "PATH": PATH_ENV_VAR,
    }
)
ENV_VARS.update(FAASM_BUILD_ENV_DICT)

LIB_SRC_DIR = join(CPYTHON_INSTALL_DIR, "lib")
LIB_DEST_DIR = join(FAASM_RUNTIME_ROOT, "lib")

LIBPYTHON_SRC_PATH = join(LIB_SRC_DIR, "libpython3.8.a")
LIBPYTHON_DEST_PATH = join(WASM_LIB_INSTALL, "libpython3.8.a")

INCLUDE_SRC_DIR = join(CPYTHON_INSTALL_DIR, "include", "python3.8")
INCLUDE_DEST_DIR = join(WASM_HEADER_INSTALL, "python3.8")

# See the CPython docs for more info:
# - General: https://devguide.python.org/setup/#compile-and-build
# - Static builds: https://wiki.python.org/moin/BuildStatically


def _run_cpython_cmd(label, cmd_array):
    # Unfortunately, building CPython with SIMD leads to some errors with
    # frozen bytecode. Thus, we manually strip it out here
    cmd_str = " ".join(cmd_array)
    patt = compile(r"(\s*)-msimd128")
    cmd_str = patt.sub("", cmd_str)
    print("CPYTHON BUILD STEP: {}".format(label))
    print(cmd_str)

    run(cmd_str, shell=True, check=True, cwd=CPYTHON_SRC, env=ENV_VARS)


@task()
def wasm(ctx, clean=False, noconf=False, nobuild=False):
    """
    Cross-compile and install the CPython runtime to WebAssembly
    """
    if exists(join(CPYTHON_SRC, "Makefile")) and clean:
        _run_cpython_cmd("clean", ["make", "clean"])

    # Shared compiler and liker arguments are used to build all C-extensions
    # in both the CPython and module builds. However, in the CPython build we
    # statically link all the C-extensions we need, therefore these are only
    # relevant in the module builds.

    # Link in extra wasi-libc long double support (see wasi-libc docs)
    link_libs = "-lc-printscan-long-double -lfaasm"

    # Configure
    configure_cmd = build_config_cmd(
        [
            "CONFIG_SITE=./config.site",
            "READELF=true",
            "./configure",
            'LIBS="{}"'.format(link_libs),
            "--disable-ipv6",
            "--disable-shared",
            "--prefix={}".format(CPYTHON_INSTALL_DIR),
            "--with-system-ffi",
        ]
    )

    if not noconf:
        _run_cpython_cmd("configure", configure_cmd)

    if not nobuild:
        # Copy in extra undefs
        _run_cpython_cmd(
            "modify", ["cat", "pyconfig-extra.h", ">>", "pyconfig.h"]
        )

        make_cmd = [
            "make -j {}".format(USABLE_CPUS),
        ]
        _run_cpython_cmd("make", make_cmd)
        _run_cpython_cmd("libpython", ["make", LIBPYTHON_NAME])

    # Run specific install tasks (see cpython/Makefile)
    _run_cpython_cmd("commoninstall", ["make", "commoninstall"])
    _run_cpython_cmd("bininstall", ["make", "bininstall"])

    # Prepare destinations
    makedirs(WASM_HEADER_INSTALL, exist_ok=True)
    makedirs(WASM_LIB_INSTALL, exist_ok=True)

    rmtree(INCLUDE_DEST_DIR, ignore_errors=True)

    print(
        "Copying libpython from {} to {}".format(
            LIBPYTHON_SRC_PATH, LIBPYTHON_DEST_PATH
        )
    )
    print(
        "Copying includes from {} to {}".format(
            INCLUDE_SRC_DIR, INCLUDE_DEST_DIR
        )
    )

    copy(LIBPYTHON_SRC_PATH, LIBPYTHON_DEST_PATH)
    copytree(INCLUDE_SRC_DIR, INCLUDE_DEST_DIR)

    makedirs(LIB_DEST_DIR, exist_ok=True)

    print("Copying contents of {} to {}".format(LIB_SRC_DIR, LIB_DEST_DIR))
    run(
        "cp -r {}/* {}/".format(LIB_SRC_DIR, LIB_DEST_DIR),
        shell=True,
        check=True,
    )


@task()
def native(ctx, clean=False):
    """
    Build and install the native CPython runtime

    We need the versions of the python runtimes in the build and host (wasm) to
    match, so we install the build python runtime manually instead of using
    APT. Note that we use the GNU terminology for cross-compiling where:
    - host: machine we are cross-compiling to (WASM)
    - build: machine we are cross-compiling from
    """
    if clean:
        rmtree(PYTHON_INSTALL_DIR)

    if not exists(PYTHON_INSTALL_DIR):
        makedirs(PYTHON_INSTALL_DIR)

    workdir = "/tmp"
    tar_name = "{}.tgz".format(PYTHON_VERSION)
    tar_url = "https://www.python.org/ftp/python/{}/{}".format(
        PYTHON_VERSION.split("-")[1], tar_name
    )
    run("wget {}".format(tar_url), shell=True, check=True, cwd=workdir)
    run("tar -xf {}".format(tar_name), shell=True, check=True, cwd=workdir)

    workdir = join(workdir, PYTHON_VERSION)
    native_configure_cmd = [
        'CC="clang-13"',
        'CXX="clang++-13"',
        'CFLAGS="-O3 -DANSI"',
        'LD="clang-13"',
        "./configure",
        "--prefix={}".format(PYTHON_INSTALL_DIR),
    ]
    # configure_cmd = "./configure --prefix={}".format(PYTHON_INSTALL_DIR)
    native_configure_cmd = " ".join(native_configure_cmd)
    print(native_configure_cmd)
    run(native_configure_cmd, shell=True, check=True, cwd=workdir)
    make_cmd = "make -j {} altinstall".format(USABLE_CPUS)
    run(make_cmd, shell=True, check=True, cwd=workdir)

    # Sanity check
    python_bin = join(PYTHON_INSTALL_DIR, "bin", "python3.8")
    pip_bin = join(PYTHON_INSTALL_DIR, "bin", "pip3.8")
    out = (
        run("{} --version".format(python_bin), shell=True, capture_output=True)
        .stdout.decode("utf-8")
        .strip()
    )
    print(out)
    out = (
        run("{} --version".format(pip_bin), shell=True, capture_output=True)
        .stdout.decode("utf-8")
        .strip()
    )
    print(out)


@task()
def func(ctx, clean=False, debug=False):
    """
    Compile the CPython entrypoint function to WASM
    """
    func_dir = join(PROJ_ROOT, "func", "cpp")
    func_build_dir = join(PROJ_ROOT, "build", "func")
    wasm_file = join(func_build_dir, "{}.wasm".format(CPYTHON_FUNC_NAME))

    # Build and install the wasm
    wasm_cmake(func_dir, func_build_dir, CPYTHON_FUNC_NAME, clean, debug)
    wasm_copy_upload(CPYTHON_FUNC_USER, CPYTHON_FUNC_NAME, wasm_file)


@task
def upload(ctx):
    """
    Upload the CPython function
    """
    host, port = get_faasm_upload_host_port()
    wasm_file = join(
        WASM_DIR, CPYTHON_FUNC_USER, CPYTHON_FUNC_NAME, "function.wasm"
    )
    url = "http://{}:{}/f/{}/{}".format(
        host, port, CPYTHON_FUNC_USER, CPYTHON_FUNC_NAME
    )
    print(
        "Uploading {}/{} to {}".format(
            CPYTHON_FUNC_USER, CPYTHON_FUNC_NAME, url
        )
    )
    response = put(url, data=open(wasm_file, "rb"))

    print("Response ({}): {}".format(response.status_code, response.text))
