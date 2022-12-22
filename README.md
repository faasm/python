# Faasm Python Environment [![Tests](https://github.com/faasm/python/workflows/Tests/badge.svg?branch=main)](https://github.com/faasm/python/actions)  [![License](https://img.shields.io/github/license/faasm/python.svg)](https://github.com/faasm/python/blob/main/LICENSE.md)

This build cross-compiles CPython and a number of Python modules to WebAssembly
for use in [Faasm](https://github.com/faasm/faasm).

It also provides [`pyfaasm`, a small Python library](pyfaasm/) which uses
`ctypes` to support calls to the [Faasm host
interface](https://faasm.readthedocs.io/en/latest/source/host_interface.html).

## Development

Most use of this project is via the Faasm [development
environment](https://faasm.readthedocs.io/en/latest/source/development.html).

You should only need the instructions below if you want to:

- [Modify the Faasm CPython runner](#building-cpython-and-libraries)
- [Change the Faasm Python host interface (`pyfaasm`)](#change-the-python-host-interface).
- Add Python libraries to the Faasm environment

### Building CPython and libraries

Faasm runs python code by cross-compiling the CPython runtime to WebAssembly,
and adding a small entrypoint function to run Python code on the cross-compiled
runtime.

To cross-compile the CPython runtime, we first need to install a native CPython
of the _exact_ same version:

```bash
inv cpython.native
```

Then, you can cross-compile CPython from our [fork](
https://github.com/faasm/cpython):

```bash
inv cpython.wasm
```

This generates a static version of `libpython` that we link to the entrypoint
function. To cross-compile this entrypoint function you can run:

```bash
inv cpython.func
```

### Change the Python host interface

Faasm provides a small python library, `pyfaasm` so that functions written in
Python (which are _not_ cross-compiled to WebAssembly) can communicate with the
Faasm runtime.

To install `pyfaasm` we need to use the same `pip` version we installed
natively (and cross-compiled) as part of the CPython build in the previous
section. Setuptools and distutils, pip's tooling to install libraries,
interrogate the system environment during the library install process. This
makes it quite difficult to install `pyfaasm` at the right location, using the
right version of `pip`. We use [crossenv](https://github.com/benfogle/crossenv)
to help with that.

To install `pyfaasm` we need to activate the `crossenv` virtual environment, we
do so in a separate shell inside the container for simplicity:

```bash
bash
./bin/crossenv_setup.sh
source ./cross_venv/bin/activate
pip3 install -r crossenv/requirements.txt
inv -r crossenv modules.install
exit
```

To use the `pyfaasm` library in Faasm, we still need to copy the installed
files to the right runtime location:

```bash
inv modules.copy
```

### Adding Python modules to the Faasm environment

Crossenv picks up the cross-compilation environment from the CPython
build artifacts. Therefore, to make changes to the cross-compilation
environment:

- Modify the CPython build (see [`tasks/cpython.py`](./tasks/cpython.py))
- Rerun the CPython build (`inv cpython.wasm --clean`)
- Rebuild the crossenv (`./bin/crossenv_setup.sh`)
- Enter the crossenv and inspect the environment with `bin/sanity_check.py`

With the crossenv activated, we can build modules with normal `pip`.

There is a wrapper script that will apply modifications if we know about them.
To run this you must first have the cross-env activated as described above.

```bash
# Install all supported modules
inv modules.install

# Install experimental modules
inv modules.install --experimental

# Install numpy
inv modules.install --name numpy

# (Attempt) to install arbitrary module
inv modules.install --name <module_name>
```

Libraries will then be installed to
`cross_venv/cross/lib/python3.8/site-packages`.

#### Debugging module builds

You can debug module builds by running `python setup.py install` through your
debugger.

You can also set `DISTUTILS_DEBUG=1` to get distutils to print more info.

#### Experimental modules

Some of the modules are experimental, these may require some extra set-up.

##### MXNet and Horovod

To install the Python MXNet module we first need to cross-compile the MXNet
shared library:

```
# Update all submodules
cd third-party/mxnet
git submodule update --init
cd ../horovod
git submodule update --init

# Run our MXNet cross-compile (outside crossenv)
cd ../..
inv mxnet
```

Then we can install mxnet and horovod:

```
. ./cross_venv/bin/activate
inv libs.install --name mxnet
inv libs.install --name horovod
```

To clean and uninstall:

```
# Clean then rebuild
inv mxnet --clean

# Uninstall mxnet
inv mxnet.uninstall
```

##### Numpy

Faasm's NumPy build relies on BLAS and LAPACK support. The right cross-compiled
libraries should be picked up by numpy due to the addition of the [site.cfg
](../third-party/numpy/site.cfg).

> 22/12/2022 - NumPy support is currently broken

## Code changes

The CPython build uses this slightly modified [fork of
CPython](https://github.com/faasm/cpython/tree/faasm).

To see the changes made to CPython, see [this
compare](https://github.com/python/cpython/compare/v3.8.2...faasm:faasm).

A similar (small) list of changes for numpy can be seen
[here](https://github.com/numpy/numpy/compare/v1.19.2...faasm:faasm).

CPython is built statically, some notes on this process can be found
[here](https://wiki.python.org/moin/BuildStatically).

Several of the code changes to CPython and numpy were borrowed from
[pyodide](https://github.com/iodide-project/pyodide).

## Releasing

This repo gets built as a container, `faasm/cpython`. If you want to release a
new version, you can:

- Bump the code version with: `inv git.bump`
- Commit to your branch
- Run `inv git.tag`
- Check the release build has run
- Create a pull request

The release build will generate a docker image with the new tag. You can also
trigger the image build manually with:

```bash
inv docker.build [--push] [--nocache]
```

