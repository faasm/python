from invoke import task
from os.path import join

from faasmtools.docker import (
    build_container,
    push_container,
)

from tasks.env import (
    PROJ_ROOT,
    get_version,
)

CONTAINER_IMAGE = "faasm/cpython"
DOCKERFILE = join(PROJ_ROOT, "docker", "cpython.dockerfile")


def _get_tag():
    tag_name = "{}:{}".format(CONTAINER_IMAGE, get_version())
    return tag_name


@task(default=True)
def build(ctx, nocache=False, push=False):
    """
    Build current version of the cpython container
    """
    version = get_version()

    build_container(
        _get_tag(),
        DOCKERFILE,
        PROJ_ROOT,
        nocache=nocache,
        push=push,
        build_args={
            "FAASM_CPYTHON_VERSION": version,
        },
    )


@task
def push(ctx):
    """
    Push the current version of the cpython container
    """
    push_container(_get_tag())
