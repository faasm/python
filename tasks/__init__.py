from invoke import Collection

from . import (
    container,
    cpython,
    libs,
    mxnet,
    ffi,
)

ns = Collection(
    container,
    cpython,
    libs,
    mxnet,
    ffi,
)
