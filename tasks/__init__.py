from invoke import Collection

from . import (
    cpython,
    libs,
    mxnet,
    ffi,
)

ns = Collection(
    cpython,
    libs,
    mxnet,
    ffi,
)
