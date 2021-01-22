import os
import ctypes

# For a tutorial on ctypes, see here:
# https://docs.python.org/3/library/ctypes.html
#
# Faasm host interface:
# https://github.com/faasm/faasm/blob/master/include/faasm/host_interface.h

NATIVE_SUPPORTING_LIBS = [
    "libpistache.so",
    "libfaabricmpi.so",
]

NATIVE_INTERFACE_LIB = "libemulator.so"

env_cache = dict()

input_data = None
output_data = None

_host_interface = None


def get_env_bool(var_name):
    global env_cache

    if var_name not in env_cache:
        value = os.environ.get(var_name)
        env_cache[var_name] = bool(value)

    return env_cache[var_name]


def set_env_bool(var_name, value):
    global env_cache
    env_cache[var_name] = value


def is_wasm():
    return get_env_bool("PYTHONWASM")


def is_local_chaining():
    return get_env_bool("PYTHON_LOCAL_CHAINING")


def is_local_output():
    return get_env_bool("PYTHON_LOCAL_OUTPUT")


def set_local_chaining(value):
    set_env_bool("PYTHON_LOCAL_CHAINING", value)


def set_local_input_output(value):
    set_env_bool("PYTHON_LOCAL_OUTPUT", value)


def _init_host_interface():
    global _host_interface

    if _host_interface is None:
        # Wasm and native environments are different
        if is_wasm():
            # Wasm expects the main application to handle the relevant calls
            _host_interface = ctypes.CDLL(None)
        else:
            # Load all supporting libs as globally linkable
            for lib in NATIVE_SUPPORTING_LIBS:
                ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)

            # Load main Faasm host interface lib
            _host_interface = ctypes.CDLL(NATIVE_INTERFACE_LIB)


def get_input_len():
    _init_host_interface()
    return _host_interface.__faasm_read_input(None, 0)


def read_input(input_len):
    _init_host_interface()
    input_len = int(input_len)
    buff = ctypes.create_string_buffer(input_len)
    return _host_interface.__faasm_read_input(buff, input_len)


def write_output(output):
    if is_local_output():
        global output_data
        output_data = output
    else:
        _init_host_interface()
        _host_interface.__faasm_write_output(output, len(output))


def get_output():
    if is_local_output():
        global output_data
        return output_data
    else:
        raise RuntimeError(
            "Should not be getting output in non-local input/ output"
        )


def read_state_size(key):
    _init_host_interface()
    return _host_interface.__faasm_read_state(bytes(key, "utf-8"), None, 0)


def read_state(key, state_len):
    _init_host_interface()
    state_len = int(state_len)
    buff = ctypes.create_string_buffer(state_len)
    _host_interface.__faasm_read_state(bytes(key, "utf-8"), buff, state_len)

    return bytes(buff)


def read_state_offset(key, total_len, offset, offset_len):
    _init_host_interface()
    total_len = int(total_len)
    offset_len = int(offset_len)
    buff = ctypes.create_string_buffer(offset_len)
    _host_interface.__faasm_read_state_offset(
        bytes(key, "utf-8"), total_len, offset, buff, offset_len
    )

    return bytes(buff)


def write_state(key, value):
    _init_host_interface()
    _host_interface.__faasm_write_state(bytes(key, "utf-8"), value, len(value))


def write_state_offset(key, total_len, offset, value):
    _init_host_interface()
    offset = int(offset)
    total_len = int(total_len)

    _host_interface.__faasm_write_state_offset(
        bytes(key, "utf-8"), total_len, offset, value, len(value)
    )


def push_state(key):
    _init_host_interface()
    _host_interface.__faasm_push_state(bytes(key, "utf-8"))


def push_state_partial(key):
    _init_host_interface()
    _host_interface.__faasm_push_state_partial(bytes(key, "utf-8"))


def pull_state(key, state_len):
    _init_host_interface()
    state_len = int(state_len)
    _host_interface.__faasm_pull_state(bytes(key, "utf-8"), state_len)


def chain(func, input_data):
    if is_local_chaining():
        # Run function directly
        func(input_data)
        return 0
    else:
        # Call into host interface
        _init_host_interface()

        func_name = func.__name__
        return _host_interface.__faasm_chain_py(
            bytes(func_name, "utf-8"), input_data, len(input_data)
        )


def await_call(call_id):
    if is_local_chaining():
        # Calls are run immediately in local chaining
        return 0
    else:
        _init_host_interface()
        return _host_interface.__faasm_await_call(call_id)


def set_emulator_message(message_json):
    _init_host_interface()

    message_bytes = bytes(message_json, "utf-8")
    if is_local_output():
        global output_data
        output_data = None

    return _host_interface.setEmulatedMessageFromJson(message_bytes)


def set_emulator_status(success):
    _init_host_interface()
    _host_interface.__set_emulator_status(success)


def get_emulator_async_response():
    _init_host_interface()
    return _host_interface.__get_emulator_async_response()
