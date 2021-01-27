import unittest
import json
from pyfaasm.core import (
    get_input_len,
    read_input,
    set_emulator_message,
)


class TestInputs(unittest.TestCase):
    def test_input_data(self):
        expected = "blah blah foo bar"
        msg = {"user": "foo", "function": "bar", "input_data": expected}

        set_emulator_message(json.dumps(msg))

        input_len = get_input_len()
        self.assertEqual(input_len, len(expected))

        actual_bytes = read_input(input_len)
        actual = actual_bytes.decode("utf-8")

        self.assertEqual(actual, expected)

    def test_empty_input_data(self):
        msg = {"user": "foo", "function": "bar"}

        set_emulator_message(json.dumps(msg))

        input_len = get_input_len()
        self.assertEqual(input_len, 0)
