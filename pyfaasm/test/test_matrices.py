import unittest
from json import dumps
from os import makedirs
from os.path import exists
from shutil import rmtree

import numpy as np
import redis
from parameterized import parameterized

from pyfaasm.config import RESULT_MATRIX_KEY
from pyfaasm.core import set_emulator_message, get_state, set_local_chaining
from pyfaasm.matrix import subdivide_matrix_into_state, reconstruct_matrix_from_submatrices, \
    read_input_submatrix, divide_and_conquer, write_matrix_params_to_state, \
    load_matrix_conf_from_state, SUBMATRICES_KEY_A, SUBMATRICES_KEY_B, random_matrix
from pyfaasm.matrix_data import subdivide_matrix_into_files, reconstruct_matrix_from_files


class TestMatrices(unittest.TestCase):
    def setUp(self):
        self.redis = redis.Redis()
        self.redis.flushall()

        self.key_a = "matrix_tester_a"
        self.key_b = "matrix_tester_b"

        msg = {
            "user": "python",
            "function": "py_func",
            "py_user": "python",
            "py_func": "mat_mul",
        }
        msg_json = dumps(msg)
        set_emulator_message(msg_json)

        # Default matrix set-up
        self.matrix_size = 1024
        self.default_split_level = 3
        self.set_up_conf(3)

        # Enforce local chaining
        set_local_chaining(True)

    def set_up_conf(self, split_level):
        # Write and read config
        write_matrix_params_to_state(self.matrix_size, split_level)
        self.conf = load_matrix_conf_from_state()

        self.assertEqual(self.conf.matrix_size, self.matrix_size)
        self.assertEqual(self.conf.n_splits, split_level)

    def test_matrix_round_trip(self):
        mat_a = random_matrix(self.conf.matrix_size)
        subdivide_matrix_into_state(self.conf, mat_a, self.key_a)
        actual = reconstruct_matrix_from_submatrices(self.conf, self.key_a)

        np.testing.assert_array_equal(mat_a, actual)

    @parameterized.expand([
        (0,), (1,), (2,), (3,),
    ])
    def test_matrix_file_round_trip(self, split_level):
        self.set_up_conf(split_level)

        mat_a = random_matrix(self.conf.matrix_size)
        mat_b = random_matrix(self.conf.matrix_size)

        file_dir = "/tmp/mat_test"
        file_prefix_a = "mat_a"
        file_prefix_b = "mat_b"

        if exists(file_dir):
            rmtree(file_dir)
        makedirs(file_dir)

        subdivide_matrix_into_files(self.conf, mat_a, file_dir, file_prefix_a)
        subdivide_matrix_into_files(self.conf, mat_b, file_dir, file_prefix_b)

        actual_a = reconstruct_matrix_from_files(self.conf, file_dir, file_prefix_a)
        actual_b = reconstruct_matrix_from_files(self.conf, file_dir, file_prefix_b)

        np.testing.assert_array_equal(mat_a, actual_a)
        np.testing.assert_array_equal(mat_b, actual_b)

    @parameterized.expand([
        (0,), (1,), (2,), (3,),
    ])
    def test_reading_submatrix_from_state(self, split_level):
        self.set_up_conf(split_level)

        mat_a = random_matrix(self.conf.matrix_size)
        mat_b = random_matrix(self.conf.matrix_size)

        subdivide_matrix_into_state(self.conf, mat_a, self.key_a)
        subdivide_matrix_into_state(self.conf, mat_b, self.key_b)

        if split_level == 0:
            row_idx = 0
            col_idx = 0
        elif split_level == 1:
            row_idx = 1
            col_idx = 1
        elif split_level == 2:
            row_idx = 3
            col_idx = 2
        else:
            row_idx = 5
            col_idx = 6

        sm_size = self.conf.get_submatrix_size(split_level)

        # Get the submatrix directly from the original
        row_start = row_idx * sm_size
        col_start = col_idx * sm_size
        expected_a = mat_a[
                     row_start:row_start + sm_size,
                     col_start:col_start + sm_size,
                     ]

        expected_b = mat_b[
                     row_start:row_start + sm_size,
                     col_start:col_start + sm_size,
                     ]

        actual_a = read_input_submatrix(self.conf, self.key_a, row_idx, col_idx)
        actual_b = read_input_submatrix(self.conf, self.key_b, row_idx, col_idx)

        np.testing.assert_array_equal(expected_a, actual_a)
        np.testing.assert_array_equal(expected_b, actual_b)

    @parameterized.expand([
        (0,), (1,), (2,), (3,),
    ])
    def test_distributed_multiplication(self, split_level):
        self.set_up_conf(split_level)

        # Set up the problem
        mat_a = random_matrix(self.conf.matrix_size)
        mat_b = random_matrix(self.conf.matrix_size)
        subdivide_matrix_into_state(self.conf, mat_a, SUBMATRICES_KEY_A)
        subdivide_matrix_into_state(self.conf, mat_b, SUBMATRICES_KEY_B)

        expected = np.dot(mat_a, mat_b)

        # Invoke the divide and conquer
        divide_and_conquer()

        # Load the result
        actual_bytes = get_state(RESULT_MATRIX_KEY, self.conf.bytes_per_matrix)
        actual = np.frombuffer(actual_bytes, dtype=np.float32).reshape(self.conf.matrix_size, self.conf.matrix_size)

        # Note that the floating point errors can creep up so we have a relatively high tolerance here
        np.testing.assert_array_almost_equal_nulp(actual, expected, nulp=20)
