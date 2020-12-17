import unittest

from pyfaasm.core import (
    write_state,
    push_state,
    pull_state,
    read_state,
    write_state_offset,
    read_state_offset,
    read_state_size,
)


class TestState(unittest.TestCase):
    def test_state_read_write(self):
        key = "pyStateTest"
        full_value = b"0123456789"
        write_state(key, full_value)
        push_state(key)

        expected_value_len = 10
        value_len = read_state_size(key)
        self.assertEqual(expected_value_len, value_len)

        # Read state back in
        pull_state(key, value_len)
        actual = read_state(key, value_len)

        # Check values as expected
        self.assertEqual(full_value, actual)

        # Update a segment
        segment = b"999"
        offset = 2
        segment_len = 3
        modified_value = b"0199956789"
        write_state_offset(key, value_len, offset, segment)

        # Push and pull
        push_state(key)
        pull_state(key, value_len)

        # Check full value as expected
        actual = read_state(key, value_len)
        self.assertEqual(modified_value, actual)

        # Check getting a segment
        actual_segment = read_state_offset(key, value_len, offset, segment_len)
        self.assertEqual(segment, actual_segment)
