from invoke import Collection

from . import (
    container,
    cpython,
    git,
    libs,
    mxnet,
    pyfaasm,
)

ns = Collection(
    container,
    cpython,
    git,
    libs,
    mxnet,
    pyfaasm,
)
