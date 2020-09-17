# Faasm CPython build

The CPython build uses the following forks:

- [CPython](https://github.com/Shillaker/cpython/tree/faasm)
- [Numpy](https://github.com/Shillaker/numpy/tree/faasm)

To avoid having to dynamically link C-extensions from Python modules, we build 
CPython and all requires modules as a single static WebAssembly library.

Some notes on building CPython statically can be found
[here](https://wiki.python.org/moin/BuildStatically). The Faasm CPython build 
adopts some of the changes made in 
[pyodide](https://github.com/iodide-project/pyodide).

## Building CPython on the build machine

To cross-compile CPython and any C-extensions, you need to have the _exact_ 
same version of Python installed on your build machine. To do this, run:

```
cd ansible
ansible-playbook python3_8.yml
```

This will install Python at `/usr/local/faasm/python3.8`.

When cross-compiling we _have_ to use this Python when running commands and
scripts on the build machine (not any other Python that might be installed).

## Building CPython to WebAssembly

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

### Crossenv set-up

To set up crossenv for the first time:

```
inv crossenv
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

