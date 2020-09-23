# Faasm CPython build

The CPython build uses a fork of 
[CPython](https://github.com/Shillaker/cpython/tree/faasm) along with other
Python module forks in the `third-party` directory.

It uses the [Faasm toolchain](https://github.com/Shillaker/faasm-toolchain) to 
build CPython and C-extensions to WebAssembly (for use with 
[Faasm](https://github.com/lsds/faasm)).

CPython is built statically, some notes on this process can be found 
[here](https://wiki.python.org/moin/BuildStatically). The Faasm CPython build 
borrows a lot of configuration from 
[pyodide](https://github.com/iodide-project/pyodide).

## Set-up

### Submodules

Make sure all the repo's submodules are initialised:

```
git submodule update --init
```

### CPython on the build machine

To cross-compile CPython and any C-extensions, the version you're cross
compiling and the version on the build machine need to match _exactly_.
To set up the relevant build machine python:

```
cd ansible
ansible-playbook python3_8.yml
```

This will install Python at `/usr/local/faasm/python3.8`.

When cross-compiling we _have_ to use this Python when running commands and
scripts on the build machine (not any other Python that might be installed).

### Building CPython to WebAssembly

You can build CPython by running (with optional `--clean`):

```
inv cpython
```

The result is installed at `third-party/cpython/install/wasm`.

We provide a [Setup.local](third-party/cpython/Modules/Setup.local) file, which
specifies which standard CPython modules will be built statically. 

At the end of the CPython build, it will print out a list of which modules have
been successfully built and which have failed. Note that many of the standard 
library modules will fail in this build, but the ones we need should succeed.

## Cross-compilation set-up

Setuptools and distutils both interrogate the Python system environment during
the build process. This makes it quite difficult to cross-compile libraries, so
we use [crossenv](https://github.com/benfogle/crossenv).

To set up crossenv:

```
./scripts/crossenv_setup.sh
```

You can then activate with:

```
. cross_venv/bin/activate
```

From inside the virtual environment, you can inspect the set-up with:

```
python scripts/sanity_check.py | less
```

This will display the environment used to install Python modules (including the
relevant cross-compilation variables, e.g. `CC`, `CFLAGS` etc.).

### Changing the crossenv environment

Crossenv picks up the cross-compilation environment from the CPython 
build artifacts. Therefore, to make changes to the cross-compilation 
environment:

- Modify the CPython build (see `tasks.py`)
- Rerun the CPython build (`inv cpython --clean`) 
- Rebuild the crossenv (`./scripts/crossenv_setup.sh`) 
- Enter the crossenv and inspect the environment with `scripts/sanity_check.py`

## Modules

With the crossenv activated, we can build modules with normal `pip`.

To install all the modules, you can run:

```
# NOTE: run this from a clean terminal, _not_ through the Faasm CLI
./scripts/install_modules.sh
```

Libraries will then be installed to 
`cross_venv/cross/lib/python3.8/site-packages`.

### Debugging module builds

You can debug module builds by running `python setup.py install` through your
debugger.

You can also set `DISTUTILS_DEBUG=1` to get distutils to print more info.

## Running in Faasm

See the [Faasm python
docs](https://github.com/lsds/faasm/blob/master/docs/python.md).

