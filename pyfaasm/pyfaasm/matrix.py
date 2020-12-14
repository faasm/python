import numpy as np
from numpy import int32

from pyfaasm.config import MATRIX_CONF_STATE_KEY, SUBMATRICES_KEY_A, SUBMATRICES_KEY_B, MatrixConf, RESULT_MATRIX_KEY
from pyfaasm.core import set_state, get_state, chain_this_with_input, await_call
from pyfaasm.matrix_data import do_subdivide_matrix, do_reconstruct_matrix


def write_matrix_params_to_state(matrix_size, n_splits):
    params = np.array((matrix_size, n_splits), dtype=int32)
    set_state(MATRIX_CONF_STATE_KEY, params.tobytes())


def load_matrix_conf_from_state():
    # Params are ints so need to work out what size they are
    dummy = np.array((1, 2), dtype=int32)
    param_len = len(dummy.tobytes())
    param_bytes = get_state(MATRIX_CONF_STATE_KEY, param_len)
    params = np.frombuffer(param_bytes, dtype=int32)

    matrix_size = params[0]
    n_splits = params[1]

    conf = MatrixConf(matrix_size, n_splits)

    return conf


def random_matrix(size):
    return np.random.rand(size, size).astype(np.float32)


# Split up the original matrix into square submatrices and write to state
def subdivide_matrix_into_state(conf, mat, key_prefix):
    def _write_submatrix_to_state(sm_bytes, row_idx, col_idx):
        full_key = conf.get_submatrix_key(key_prefix, conf.n_splits, row_idx, col_idx)
        set_state(full_key, sm_bytes)

    do_subdivide_matrix(conf, mat, _write_submatrix_to_state)


# Reads a given submatrix from the input
def read_input_submatrix(conf, key_prefix, row_idx, col_idx):
    sm_bytes = conf.get_bytes_per_submatrix(conf.n_splits)
    sm_size = conf.get_submatrix_size(conf.n_splits)
    full_key = conf.get_submatrix_key(key_prefix, conf.n_splits, row_idx, col_idx)

    sub_mat_data = get_state(full_key, sm_bytes)
    return np.frombuffer(sub_mat_data, dtype=np.float32).reshape(sm_size, sm_size)


# Rebuilds a matrix from its submatrices in state
def reconstruct_matrix_from_submatrices(conf, key_prefix):
    def _read_submatrix_from_state(row_idx, col_idx):
        full_key = conf.get_submatrix_key(key_prefix, conf.n_splits, row_idx, col_idx)
        sm_bytes = conf.get_bytes_per_submatrix(conf.n_splits)
        return get_state(full_key, sm_bytes)

    return do_reconstruct_matrix(conf, _read_submatrix_from_state)


# This is the distributed worker that will be invoked by faasm
def distributed_divide_and_conquer(input_bytes):
    conf = load_matrix_conf_from_state()

    input_args = np.frombuffer(input_bytes, dtype=int32)

    split_level = input_args[0]
    row_a = input_args[1]
    col_a = input_args[2]
    row_b = input_args[3]
    col_b = input_args[4]

    # If we're at the target number of splits, do the work
    if split_level == conf.n_splits:
        # Read in the relevant submatrices of each input matrix
        mat_a = read_input_submatrix(conf, SUBMATRICES_KEY_A, row_a, col_a)
        mat_b = read_input_submatrix(conf, SUBMATRICES_KEY_B, row_b, col_b)

        # Do the multiplication in memory
        result = np.dot(mat_a, mat_b)
    else:
        # Recursively kick off more divide and conquer
        result = chain_multiplications(conf, split_level, row_a, col_a, row_b, col_b)

    # Write the result
    result_key = conf.get_intermediate_result_key(split_level, row_a, col_a, row_b, col_b)
    set_state(result_key, result.tobytes())


def divide_and_conquer():
    conf = load_matrix_conf_from_state()
    print("Running divide and conquer for {}x{} matrix with {} splits".format(
        conf.matrix_size,
        conf.matrix_size,
        conf.n_splits
    ))

    # Short-cut for no splits
    if conf.n_splits == 0:
        # Read in the relevant submatrices of each input matrix
        mat_a = read_input_submatrix(conf, SUBMATRICES_KEY_A, 0, 0)
        mat_b = read_input_submatrix(conf, SUBMATRICES_KEY_B, 0, 0)

        # Do the multiplication in memory
        result = np.dot(mat_a, mat_b)
    else:
        # Kick off the basic multiplication jobs
        result = chain_multiplications(conf, 0, 0, 0, 0, 0)

    # Write final result
    set_state(RESULT_MATRIX_KEY, result.tobytes())


def get_addition_result(conf, split_level, addition_def):
    sm_size = conf.get_submatrix_size(split_level)
    sm_byte_size = conf.get_bytes_per_submatrix(split_level)

    key_a = conf.get_intermediate_result_key(split_level,
                                             addition_def[0][0][0], addition_def[0][0][1],
                                             addition_def[0][1][0], addition_def[0][1][1],
                                             )

    key_b = conf.get_intermediate_result_key(split_level,
                                             addition_def[1][0][0], addition_def[1][0][1],
                                             addition_def[1][1][0], addition_def[1][1][1],
                                             )

    bytes_a = get_state(key_a, sm_byte_size)
    mat_a = np.frombuffer(bytes_a, dtype=np.float32).reshape(sm_size, sm_size)

    bytes_b = get_state(key_b, sm_byte_size)
    mat_b = np.frombuffer(bytes_b, dtype=np.float32).reshape(sm_size, sm_size)

    return mat_a + mat_b


def chain_multiplications(conf, split_level, row_a, col_a, row_b, col_b):
    """
    Spawns 8 workers to do the relevant multiplication in parallel.
    - split level is how many times we've split the original matrix
    - row_a, col_a is the chunk of matrix A
    - row_b, col_b is the chunk of matrix B

    The row/ col values will specify which chunk of the current split level, not
    actual indices in the final input matrices. Those must only be calculated
    when the final multiplication is done.
    """
    call_ids = []

    # Next split down we'll double the number of submatrices
    next_split_level = split_level + 1
    next_row_a = 2 * row_a
    next_row_b = 2 * row_b
    next_col_a = 2 * col_a
    next_col_b = 2 * col_b

    # Splitting submatrix A into four, A11, A12, A21, A22 and same with B
    a11 = [next_row_a, next_col_a]
    a12 = [next_row_a, next_col_a + 1]
    a21 = [next_row_a + 1, next_col_a]
    a22 = [next_row_a + 1, next_col_a + 1]

    b11 = [next_row_b, next_col_b]
    b12 = [next_row_b, next_col_b + 1]
    b21 = [next_row_b + 1, next_col_b]
    b22 = [next_row_b + 1, next_col_b + 1]

    # Define the relevant multiplications and additions for these submatrices
    additions = [
        [(a11, b11), (a12, b21)], [(a11, b12), (a12, b22)],
        [(a21, b11), (a22, b21)], [(a21, b12), (a22, b22)],
    ]

    # Build a list of all the required multiplications
    multiplications = list()
    for mult_one, mult_two in additions:
        multiplications.append(mult_one)
        multiplications.append(mult_two)

    # Kick off the multiplications in parallel
    for submatrix_a, submatrix_b in multiplications:
        inputs_a = np.array([
            next_split_level,
            submatrix_a[0], submatrix_a[1],
            submatrix_b[0], submatrix_b[1],
        ], dtype=int32)

        call_ids.append(chain_this_with_input(
            distributed_divide_and_conquer,
            inputs_a.tobytes())
        )

    # Await completion
    for call_id in call_ids:
        await_call(call_id)

    # Go through and get the results
    r_1 = get_addition_result(conf, next_split_level, additions[0])
    r_2 = get_addition_result(conf, next_split_level, additions[1])
    r_3 = get_addition_result(conf, next_split_level, additions[2])
    r_4 = get_addition_result(conf, next_split_level, additions[3])

    # Reconstitute the result
    result = np.concatenate((
        np.concatenate((r_1, r_2), axis=1),
        np.concatenate((r_3, r_4), axis=1)
    ), axis=0)

    return result
