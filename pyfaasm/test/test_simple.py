import unittest
from pyfaasm.core import check_python_bindings


class TestSimple(unittest.TestCase):

    def test_simple_bindings(self):
        # Just check this doesn't error
        check_python_bindings()
