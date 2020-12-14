import unittest

from pyfaasm.core import set_state, push_state, pull_state, get_state, set_state_offset, get_state_offset, get_state_size


class TestState(unittest.TestCase):

    def test_state_read_write(self):
        key = "pyStateTest"
        full_value = b'0123456789'
        set_state(key, full_value)
        push_state(key)

        expected_value_len = 10
        value_len = get_state_size(key)
        self.assertEqual(expected_value_len, value_len)

        # Read state back in
        pull_state(key, value_len)
        actual = get_state(key, value_len)

        # Check values as expected
        self.assertEqual(full_value, actual)

        # Update a segment
        segment = b'999'
        offset = 2
        segment_len = 3
        modified_value = b'0199956789'
        set_state_offset(key, value_len, offset, segment)

        # Push and pull
        push_state(key)
        pull_state(key, value_len)

        # Check full value as expected
        actual = get_state(key, value_len)
        self.assertEqual(modified_value, actual)

        # Check getting a segment
        actual_segment = get_state_offset(key, value_len, offset, segment_len)
        self.assertEqual(segment, actual_segment)
