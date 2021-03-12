try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PKG_NAME = "pyfaasm"


def main():
    long_description = """
## Faasm Python Bindings
See main repo at https://github.com/faasm/faasm
    """

    setup(
        name=PKG_NAME,
        packages=[PKG_NAME],
        version="0.0.1",
        description="Python interface for Faasm",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Simon S",
        author_email="foo@bar.com",
        url="https://github.com/faasm/python",
    )


if __name__ == "__main__":
    main()
