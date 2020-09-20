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

## Cross-compiling modules

Setuptools and distutils both interrogate the Python system environment during
the build process. This makes it quite difficult to cross-compile libraries, so
we use [crossenv](https://github.com/benfogle/crossenv).

### Crossenv set-up

To set up crossenv for the first time:

```
./crossenv.sh
```

You can then activate with:

```
. cross_venv/bin/activate
```

### Building modules

With the crossenv activated, we can build modules with normal `pip`:

```
cd third-party/numpy
pip install .
```

To get the pip logs add the `--log` argument.

```
pip install . --log /tmp/pip.log
```

### Crossenv environment issues

Note that crossenv should pick up _most_ of the required cross-compilation
environment from the CPython build artifacts. The bits that it doesn't pick up
will be set in `crossenv.sh`, so check _both_ when debugging issues.

The config seen by crossenv will be echoed in 
`cross_venv/lib/_sysconfigdata_wasi_.py`. 

Because crossenv picks up its info from the CPython build, any changes, to the 
cross-compile environment must be replicated in the CPython build.

### Runtime files

CPython needs to access certain files at runtime. These can be put in place with
the following:

```
inv runtime
```

