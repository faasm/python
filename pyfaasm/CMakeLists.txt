cmake_minimum_required(VERSION 3.0)
project(cfaasm)

# Override compiler target for shared lib
set(CMAKE_C_COMPILER_TARGET wasm32-unknown-emscripten)
set(CMAKE_CXX_COMPILER_TARGET wasm32-unknown-emscripten)

set(CMAKE_C_FLAGS "-fPIC -nostdlib ${CMAKE_C_FLAGS}")

set(CMAKE_SHARED_LINKER_FLAGS " \
        -Xlinker --shared \
        -Xlinker --stack-first \
        -Wl,-z,stack-size=2097152 -Wl, \
        -Xlinker --no-entry \
        -Xlinker --export-all \
        -Xlinker --export-dynamic \
        -Xlinker --no-gc-sections \
    ")

# Include CPython headers
set(PYODIDE_CPYTHON "/usr/local/code/faasm/third-party/pyodide/cpython/installs/python-3.7.0")
include_directories(${PYODIDE_CPYTHON}/include/python3.7m)

add_library(cfaasm SHARED pyfaasm/cfaasm.c)
