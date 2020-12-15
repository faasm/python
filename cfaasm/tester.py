import ctypes

SUPPORTING_LIBS = [
    "libpistache.so",
    "libfaabricmpi.so",
]

HOST_INTERFACE_LIB = "libemulator.so"


# For a tutorial on ctypes, see here:
# https://docs.python.org/3/library/ctypes.html
#
# Faasm host interface:
# https://github.com/faasm/faasm/blob/master/include/faasm/host_interface.h

_host_interface = None


def init_host_interface():
    global _host_interface

    if _host_interface is None:
        # Load all supporting libs as globally linkable
        for lib in SUPPORTING_LIBS:
            ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)

        # Load main Faasm host interface lib
        _host_interface = ctypes.CDLL("libemulator.so")
        print("Loaded Faasm host interface: {}".format(_host_interface))


def append_state():
    pass


def await_call():
    pass


def await_call_output():
    pass


def chain_name():
    pass


def chain_ptr():
    pass


def chain_py():
    pass


def clear_appended_state():
    pass


def conf_flag():
    pass


def get_py_entry():
    pass


def get_py_func():
    pass


def lock_state_global():
    pass


def lock_state_read():
    pass


def lock_state_write():
    pass


def push_state(key):
    _host_interface.__faasm_push_state(key)


def pull_state():
    pass


def push_state_partial():
    pass


def read_appended_state():
    pass


def read_input():
    return _host_interface.__faasm_read_input()


def read_state(key, state_size):
    buff = ctypes.create_string_buffer(state_size)
    _host_interface.__faasm_read_state(key, buff, state_size)
    return buff


def read_state_offset():
    pass


def read_state_ptr():
    pass


def read_state_offset_ptr():
    pass


def unlock_state_global():
    pass


def unlock_state_read(key_bytes):
    _host_interface.__faasm_unlock_state_read(key_bytes)


def unlock_state_write(key_bytes):
    _host_interface.__faasm_unlock_state_write(key_bytes)


def write_output(byte_data):
    _host_interface.__faasm_write_output(byte_data)


def write_state(key, bytes_data):
    _host_interface.__faasm_write_state(key, bytes_data, len(bytes_data))


def write_state_offset():
    pass


if __name__ == "__main__":
    key = b"foobar"
    full_value = b"0123456789"

    init_host_interface()

    write_state(key, full_value)
    push_state(key)

    actual = read_state(key, len(full_value))
    print(actual)
