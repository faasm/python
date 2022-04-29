cmake_minimum_required(VERSION 3.8.0)
project(faasm-func)

set(CMAKE_CXX_STANDARD 17)

if (CMAKE_SYSTEM_NAME STREQUAL "Wasm")
    SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} \
        -Xlinker --export=_faasm_zygote \
        -Xlinker --export=__heap_base \
        -Xlinker --export=__data_end \
        -Xlinker --export=__wasm_call_ctors \
        -Xlinker --max-memory=4294901760 \
        -Wl,-z,stack-size=4194304 -Wl, \
    ")

    SET(CMAKE_EXECUTABLE_SUFFIX ".wasm")
endif ()

if (CMAKE_SYSTEM_NAME STREQUAL "Wasm")
    set(FAASM_FUNC_LIBS faasm c-printscan-long-double)

    set(PYTHON_LIBRARIES ${CMAKE_SYSROOT}/lib/wasm32-wasi/libpython3.8.a)
    set(PYTHON_INCLUDE_DIRS ${CMAKE_SYSROOT}/include/python3.8)
else ()
    find_package(PythonLibs)
endif()

add_executable(py_func pyinit.c pyinit.h py_func.cpp)

if (CMAKE_SYSTEM_NAME STREQUAL "Wasm")
    target_link_libraries(py_func faasm emscripten c-printscan-long-double)
    target_link_libraries(py_func ${PYTHON_LIBRARIES})
    target_include_directories(py_func PUBLIC ${PYTHON_INCLUDE_DIRS})

    # Need to export all symbols to support dynamic linking C-extensions
    set_target_properties(py_func PROPERTIES
        LINK_FLAGS "-Xlinker --export-all -Xlinker --no-gc-sections"
    )
else()
    target_link_libraries(py_func ${PYTHON_LIBRARIES} util)
    target_include_directories(py_func PRIVATE ${FAASM_NATIVE_INSTALL}/include)
endif()

