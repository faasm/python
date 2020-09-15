# Faasm CPython build

The CPython build uses a [fork](https://github.com/Shillaker/cpython) of the 
main [CPython repo](https://github.com/python/cpython). The changes in the fork
live on the [`faasm` branch](https://github.com/Shillaker/cpython/tree/faasm).

To avoid having to dynamically link C-extensions from Python modules, we build 
CPython and all requires modules as a single static WebAssembly library.

Some notes on building CPython statically can be found
[here](https://wiki.python.org/moin/BuildStatically). The Faasm CPython build 
adopts some of the changes made in 
[pyodide](https://github.com/iodide-project/pyodide).

## Build Python

To cross-compile CPython and any C-extensions, you need to have the _exact_ 
same version of Python installed on your build machine. To do this, run:

```
cd ansible
ansible-playbook python3_8.yml
```

This will install Python at `/usr/local/faasm/python3.8`.

When cross-compiling we _have_ to use this Python when running commands and
scripts on the build machine (not any other Python that might be installed).

## Building CPython

You can build CPython by running:

```
inv cpython
```

The result is installed at `third-party/cpython/install/wasm`.

CPython needs to access certain files at runtime. These can be put in place with
the following:

```
inv runtime
```

## Cross-compiling modules

Setuptools and distutils both interrogate the Python system environment during
the build process. This makes it quite difficult to cross-compile libraries, so
we use [crossenv](https://github.com/benfogle/crossenv).

To set up crossenv for the first time:

```
inv crossenv
```

You can then activate with:

```
. ./cross_venv/bin/activate
```

And build modules with normal `pip`:

```
pip install numpy
```
