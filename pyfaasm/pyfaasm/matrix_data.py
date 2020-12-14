from os.path import join

import numpy as np


def subdivide_matrix_into_files(conf, mat, file_dir, file_prefix):
    def _write_submatrix_to_file(sm_bytes, row_idx, col_idx):
        file_name = conf.get_submatrix_key(file_prefix, conf.n_splits, row_idx, col_idx)
        file_path = join(file_dir, file_name)
        with open(file_path, "wb") as fh:
            fh.write(sm_bytes)

    do_subdivide_matrix(conf, mat, _write_submatrix_to_file)


def reconstruct_matrix_from_files(conf, file_dir, file_prefix):
    def _read_submatrix_from_file(row_idx, col_idx):
        file_name = conf.get_submatrix_key(file_prefix, conf.n_splits, row_idx, col_idx)
        file_path = join(file_dir, file_name)
        with open(file_path, "rb") as fh:
            file_bytes = fh.read()

        return file_bytes

    return do_reconstruct_matrix(conf, _read_submatrix_from_file)


def do_subdivide_matrix(conf, mat, write_func):
    # Step through rows and columns of original matrix, appending submatrix bytes
    # to the overall byte stream
    sm_per_row = conf.get_submatrices_per_row(conf.n_splits)
    sm_size = conf.get_submatrix_size(conf.n_splits)

    for row_idx in range(0, sm_per_row):
        for col_idx in range(0, sm_per_row):
            # Work out the position of the top left and bottom right corner of the submatrix
            row_start = row_idx * sm_size
            col_start = col_idx * sm_size

            row_end = row_start + sm_size
            col_end = col_start + sm_size

            # Extract the submatrix and write to bytes
            sub_mat = mat[row_start:row_end, col_start:col_end]
            sm_bytes = sub_mat.tobytes()
            write_func(sm_bytes, row_idx, col_idx)


def do_reconstruct_matrix(conf, read_func):
    result = None

    sm_per_row = conf.get_submatrices_per_row(conf.n_splits)
    sm_size = conf.get_submatrix_size(conf.n_splits)

    # Need to read in row by row concatenate the rows
    for row_idx in range(0, sm_per_row):
        submatrices = []
        for col_idx in range(0, sm_per_row):
            sm_data = read_func(row_idx, col_idx)
            this_submat = np.frombuffer(sm_data, dtype=np.float32)
            this_submat = this_submat.reshape(sm_size, sm_size)
            submatrices.append(this_submat)

        this_row = np.concatenate(submatrices, axis=1)

        if row_idx == 0:
            # Initialise the result
            result = this_row
        else:
            # Add the row to the existing result
            result = np.concatenate((result, this_row), axis=0)

    return result
