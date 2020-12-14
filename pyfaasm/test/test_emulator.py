import unittest
from json import dumps

from pyfaasm.core import set_local_input_output, \
    set_emulator_message, get_output, set_output, PYTHON_LOCAL_OUTPUT


class TestEmulator(unittest.TestCase):
    original_local_output = False

    @classmethod
    def setUpClass(cls):
        # Check what local output already set to
        cls.original_local_output = PYTHON_LOCAL_OUTPUT

    @classmethod
    def tearDownClass(cls):
        # Reset to original local output value
        set_local_input_output(cls.original_local_output)

    def test_local_output(self):
        set_local_input_output(True)

        # Set up the function
        msg = {
            "user": "python",
            "function": "py_func",
            "py_user": "python",
            "py_func": "echo",
        }
        json_msg = dumps(msg)
        set_emulator_message(json_msg)

        # Check output is initially empty
        self.assertIsNone(get_output())

        # Set output and check
        output_a = b'12345'
        set_output(output_a)
        self.assertEqual(get_output(), output_a)

        # Set output again and check updated
        output_b = b'666777'
        set_output(output_b)
        self.assertEqual(get_output(), output_b)

    def test_changing_function_clears_local_output(self):
        set_local_input_output(True)

        # Set output and check
        output_a = b'12345'
        set_output(output_a)
        self.assertEqual(get_output(), output_a)

        # Change function
        msg = {
            "user": "foo",
            "function": "bar",
        }
        json_msg = dumps(msg)
        set_emulator_message(json_msg)

        # Check output is now empty
        self.assertIsNone(get_output())

    def test_setting_emulator_message_returns_id(self):
        msg = {
            "user": "foo",
            "function": "bar",
        }
        json_msg = dumps(msg)
        actual = set_emulator_message(json_msg)

        self.assertGreater(actual, 0)
