# NOTE: we are careful to use 32-bit floats to ease interoperability with wasm code
NP_ELEMENT_SIZE = 4

SUBMATRICES_KEY_A = "mat_a"
SUBMATRICES_KEY_B = "mat_b"
INTERMEDIATE_RESULT_PREFIX = "intermediate"
RESULT_MATRIX_KEY = "result_matrix"
MATRIX_CONF_STATE_KEY = "matrix_state"


# Remember we're dealing with square matrices and splitting the matrix into
# four pieces each time we do the divide in the divide and conquer.
# The number of splits is how many times we're dividing the origin matrices.


class MatrixConf(object):
    def __init__(self, matrix_size, n_splits):
        self.matrix_size = matrix_size
        self.n_splits = n_splits
        self.bytes_per_matrix = (matrix_size * matrix_size) * NP_ELEMENT_SIZE

    def get_submatrices_per_row(self, split_level):
        return 2**split_level

    def get_submatrix_size(self, split_level):
        return self.matrix_size // (2**split_level)

    def get_bytes_per_submatrix(self, split_level):
        sm_size = self.get_submatrix_size(split_level)
        return sm_size * sm_size * NP_ELEMENT_SIZE

    def get_intermediate_result_key(
        self, split_level, row_a, col_a, row_b, col_b
    ):
        key = "intermediate_{}_{}_{}_{}_{}".format(
            split_level, row_a, col_a, row_b, col_b
        )
        return key

    def get_submatrix_key(self, key_prefix, split_level, row_idx, col_idx):
        full_key = "{}_{}_{}_{}".format(
            key_prefix, split_level, row_idx, col_idx
        )
        return full_key
