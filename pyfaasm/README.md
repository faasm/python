# PyFaasm

Python bindings for [Faasm](https://github.com/lsds/Faasm) host interface.

The library is normally compiled to WebAssembly in the [faasm-cpython
repo](https://github.com/faasm/faasm-cpython), but you can also compile it
natively for development.

## Developing

To build the container and run the tests:

```bash
# Build the container
python3 docker_build.py

# Run the container
docker run -it -v $(pwd):/code/pyfaasm faasm/pyfaasm /bin/bash

# Run the tests (inside the container)
./run_tests.sh
```

If you make changes to the C-extensions you need to rerun:

```
pip3 install -e .
```
