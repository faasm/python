cmake_minimum_required(VERSION 3.8.0)
project(faasm-func)

set(CMAKE_CXX_STANDARD 17)

if (CMAKE_SYSTEM_NAME STREQUAL "WASI")
    # Set the right target so that we look in the right sysroot
    set(CMAKE_C_FLAGS "--target=$ENV{FAASM_WASM_TRIPLE} ${CMAKE_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "--target=$ENV{FAASM_WASM_TRIPLE} ${CMAKE_CXX_FLAGS}")

    # For Faasm functions, we add `_faasm_zygote` as an exported symbol
    set(CMAKE_EXE_LINKER_FLAGS
        "${CMAKE_EXE_LINKER_FLAGS} -Xlinker --export=_faasm_zygote"
    )

    message(STATUS "Detected wasm build (sysroot=$ENV{FAASM_WASM_SYSROOT})")
    set(CMAKE_EXECUTABLE_SUFFIX ".wasm")
endif ()

if (CMAKE_SYSTEM_NAME STREQUAL "WASI")
    set(FAASM_FUNC_LIBS faasm emscripten c-printscan-long-double)

    set(PYTHON_LIBRARIES $ENV{FAASM_WASM_LIB_INSTALL_DIR}/libpython3.8.a)
    set(PYTHON_INCLUDE_DIRS $ENV{FAASM_WASM_HEADER_INSTALL_DIR}/python3.8)
else ()
    find_package(PythonLibs)
endif()

add_executable(py_func pyinit.c pyinit.h py_func.cpp)

if (CMAKE_SYSTEM_NAME STREQUAL "WASI")
    target_link_libraries(py_func ${FAASM_FUNC_LIBS} ${PYTHON_LIBRARIES} ffi)
    target_include_directories(py_func PUBLIC ${PYTHON_INCLUDE_DIRS})

    # Need to export all symbols to support dynamic linking C-extensions
    set_target_properties(py_func PROPERTIES
        LINK_FLAGS $ENV{FAASM_WASM_EXE_LINKER_FLAGS_SHARED}
    )
else()
    target_link_libraries(py_func ${PYTHON_LIBRARIES} util)
    target_include_directories(py_func PRIVATE ${FAASM_NATIVE_INSTALL}/include)
endif()
