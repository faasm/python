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


@task(default=True)
def build(ctx, nocache=False, push=False):
    """
    Build current version of the cpython container
    """
    tag_name = "{}:{}".format(CONTAINER_IMAGE, get_version())

    build_container(
        tag_name, DOCKERFILE, PROJ_ROOT, nocache=nocache, push=push
    )


@task
def push(ctx):
    """
    Push the current version of the cpython container
    """
    tag_name = "{}:{}".format(CONTAINER_IMAGE, get_version())
    push_container(tag_name)
