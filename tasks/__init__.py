from invoke import Collection

from . import (
    cpython,
    libs,
    mxnet,
)

ns = Collection(
    cpython,
    libs,
    mxnet,
)
