from invoke import Collection

from . import (
    container,
    cpython,
    git,
    libs,
    mxnet,
)

ns = Collection(
    container,
    cpython,
    git,
    libs,
    mxnet,
)
