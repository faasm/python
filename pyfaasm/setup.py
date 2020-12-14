from os import environ
from os.path import join

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

PKG_NAME = "pyfaasm"
FAASM_LIBS = [
    "faasm",
    "emulator",
    "faabric",
    "faabricmpi",
    "protobuf",
    "pthread",
    "pistache",
    "hiredis",
    "grpc++",
    "grpc++_reflection",
    "boost_system",
    "boost_filesystem",
]

FAASM_INSTALL = "/usr/local/faasm/native"


def main():
    # Detect whether this is a wasm build
    if environ.get("PYTHON_CROSSENV"):
        print("Detected WebAssembly build")
        is_wasm_build = True
    else:
        print("Detected native build")
        is_wasm_build = False

    extension_kwargs = {
        "sources": ["pyfaasm/cfaasm.c"],
    }

    if not is_wasm_build:
        # Include native libraries in native build to allow emulation
        extension_kwargs.update(
            {
                "libraries": FAASM_LIBS,
                "library_dirs": [join(FAASM_INSTALL, "lib")],
                "include_dirs": [join(FAASM_INSTALL, "include")],
            }
        )

    long_description = """
## Faasm Python Bindings
See main repo at https://github.com/lsds/faasm
    """

    setup(
        name=PKG_NAME,
        packages=[PKG_NAME],
        version="0.1.10",
        description="Python interface for Faasm",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Simon S",
        author_email="foo@bar.com",
        url="https://github.com/lsds/faasm",
        ext_modules=[Extension("pyfaasm.cfaasm", **extension_kwargs)],
    )


if __name__ == "__main__":
    main()
