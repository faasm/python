from os.path import join, exists 
from shutil import rmtree
from subprocess import run
from copy import copy

import os

from faasmcli.util.env import (
    FAASM_TOOLCHAIN_FILE,
    SYSROOT_INSTALL_PREFIX,
    FAASM_SYSROOT,
)
from faasmcli.util.files import clean_dir
from invoke import task
from tasks.env import THIRD_PARTY_DIR

MXNET_DIR = join(THIRD_PARTY_DIR, "mxnet")

# See the MXNet CPP guide for more info:
# https://mxnet.apache.org/api/cpp.html

INSTALLED_LIBS = [
    "mxnet",
    "dmlc",
]

INSTALLED_HEADER_DIRS = [
    join(FAASM_SYSROOT, "include", "mxnet"),
    join(FAASM_SYSROOT, "include", "dmlc"),
]

INSTALLED_LIBS_DIR = join(FAASM_SYSROOT, "lib", "wasm32-wasi")


@task
def uninstall(ctx):
    """
    Removes installed MXNet components
    """
    for lib_name in INSTALLED_LIBS:
        base_path = join(INSTALLED_LIBS_DIR, lib_name)
        lib_paths = [
            "{}.so".format(base_path),
            "{}.a".format(base_path),
        ]

        for lib_path in lib_paths:
            if exists(lib_path):
                print("Removing {}".format(lib_path))
                os.remove(lib_path)

    for header_dir in INSTALLED_HEADER_DIRS:
        if exists(header_dir):
            print("Removing {}".format(header_dir))
            rmtree(header_dir)


@task(default=True)
def install(ctx, clean=False, shared=True):
    """
    Installs the MXNet system library
    """
    work_dir = join(MXNET_DIR, "build")

    clean_dir(work_dir, clean)

    env_vars = copy(os.environ)

    # Set up different flags for shared/ static    
    shared_flag = "ON" if shared else "OFF"

    # Note we have to build a shared lib for use with Python
    cmake_cmd = [
        "cmake",
        "-GNinja",
        "-DFAASM_BUILD_TYPE=wasm",
        "-DFAASM_BUILD_SHARED={}".format(shared_flag),
        "-DCMAKE_TOOLCHAIN_FILE={}".format(FAASM_TOOLCHAIN_FILE),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX={}".format(SYSROOT_INSTALL_PREFIX),
        "-DCMAKE_INSTALL_LIBDIR=lib/wasm32-wasi",
        "-DUSE_CUDA=OFF",
        "-DUSE_LAPACK=OFF",
        "-DUSE_MKL_IF_AVAILABLE=OFF",
        "-DUSE_F16C=OFF",
        "-DUSE_SSE=OFF",
        "-DUSE_S3=OFF",
        "-DUSE_OPENMP=OFF",
        "-DUSE_OPENCV=OFF",
        "-DUSE_INTGEMM=OFF",
        "-DUSE_TENSORRT=OFF",
        "-DUSE_OPERATOR_TUNING=OFF",
        "-DBUILD_CPP_EXAMPLES=OFF",
        "-DUSE_SIGNAL_HANDLER=OFF",
        "-DUSE_CCACHE=OFF",
        "-DUSE_CPP_PACKAGE=ON",
        "-DMXNET_BUILD_SHARED_LIBS={}".format(shared_flag),
        "-DBUILD_SHARED_LIBS={}".format(shared_flag),
        MXNET_DIR,
    ]

    cmake_str = " ".join(cmake_cmd)
    print(cmake_str)

    print("RUNNING CMAKE")
    res = run(cmake_str, shell=True, cwd=work_dir, env=env_vars)
    if res.returncode != 0:
        raise RuntimeError(
            "MXNet CMake config failed ({})".format(res.returncode)
        )

    print("RUNNING NINJA")
    res = run("ninja -v mxnet", shell=True, cwd=work_dir, env=env_vars)
    if res.returncode != 0:
        raise RuntimeError("MXNet build failed ({})".format(res.returncode))

    print("RUNNING INSTALL")
    res = run("ninja install", shell=True, cwd=work_dir)
    if res.returncode != 0:
        raise RuntimeError("MXNet install failed ({})".format(res.returncode))
