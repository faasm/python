# Faasm CPython build

The CPython build uses a fork of 
[CPython](https://github.com/Shillaker/cpython/tree/faasm) along with other
Python module forks in the `third-party` directory.

CPython is built statically, some notes on this process can be found 
[here](https://wiki.python.org/moin/BuildStatically). The Faasm CPython build 
is inspired by [pyodide](https://github.com/iodide-project/pyodide).

## Set-up

### CPython on the build machine

To cross-compile CPython and any C-extensions, you need to have the _exact_ 
same version of Python installed on your _build_ machine. To do this, run:

```
cd ansible
ansible-playbook python3_8.yml
```

This will install Python at `/usr/local/faasm/python3.8`.

When cross-compiling we _have_ to use this Python when running commands and
scripts on the build machine (not any other Python that might be installed).

### Building CPython to WebAssembly

You can build CPython by running:

```
inv cpython
```

The result is installed at `third-party/cpython/install/wasm`.

We provide a [Setup.local](third-party/cpython/Modules/Setup.local) file, which
specifies which standard CPython modules will be built statically. Many of the
non-essential standard libraries will error as part of their build, which is ok
provided we don't need them.

At the end of the CPython build, it will print out a list of which modules have 
been successfully built and which have failed.

## Cross-compilation set-up

Setuptools and distutils both interrogate the Python system environment during
the build process. This makes it quite difficult to cross-compile libraries, so
we use [crossenv](https://github.com/benfogle/crossenv).

To set up crossenv for the first time:

```
./crossenv.sh
```

You can then activate with:

```
. cross_venv/bin/activate
```

From inside the virtual environment, you can inspect the set-up with:

```
python sanity_check.py | less
```

### Changing the crossenv environment

Note that crossenv picks up the cross-compilation environment from the CPython 
build. Therefore, to make changes:

- Modify the CPython build (see `tasks.py`)
- Rerun the CPython build (`inv cpython.py --clean`) 
- Rebuild the crossenv (`./crossenv_setup.sh`) 
- Enter the crossenv and inspect the environment with `sanity_check.py`

## Modules

With the crossenv activated, we can build modules with normal `pip`,
e.g.

```
cd third-party/numpy
pip install .
```

To get the pip logs add the `--log` argument.

```
pip install . --log /tmp/pip.log
```

## Runtime files

CPython needs to access certain files at runtime. These can be put in place with
the following:

```
inv runtime
```
