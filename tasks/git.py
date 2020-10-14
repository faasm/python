from invoke import task

from faasmtools.env import get_version
from faasmtools.git import tag_project
from tasks.env import PROJ_ROOT


@task
def tag(ctx):
    """
    Creates git tag from the current tree
    """
    version = get_version()
    tag_name = "v{}".format(version)
    tag_project(tag_name, PROJ_ROOT)
