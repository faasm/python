import os

import pyfaasm.cfaasm as cf

PYTHON_LOCAL_CHAINING = bool(os.environ.get("PYTHON_LOCAL_CHAINING"))
PYTHON_LOCAL_OUTPUT = bool(os.environ.get("PYTHON_LOCAL_OUTPUT"))

input_data = None
output_data = None


def set_local_chaining(value):
    global PYTHON_LOCAL_CHAINING
    PYTHON_LOCAL_CHAINING = value


def set_local_input_output(value):
    global PYTHON_LOCAL_OUTPUT
    PYTHON_LOCAL_OUTPUT = value


def check_python_bindings():
    # This should return a valid string
    message = cf.hello_faasm()
    print(message)

    # Check the hard-coded dummy input
    actual_input = cf.check_input()
    expected_input = b'01234'
    if type(actual_input == bytes) and actual_input == expected_input:
        print("Got expected input {} (expected {})".format(actual_input, expected_input))
    else:
        print("Did not get expected input (expected {}, actual {})".format(expected_input, actual_input))


def get_input():
    return cf.faasm_get_input()


def set_output(output):
    if PYTHON_LOCAL_OUTPUT:
        global output_data
        output_data = output
    else:
        cf.faasm_set_output(output)


def get_output():
    if PYTHON_LOCAL_OUTPUT:
        global output_data
        return output_data
    else:
        raise RuntimeError("Should not be getting output in non-local input/ output")


def get_state_size(key):
    return cf.faasm_get_state_size(key)


def get_state(key, len):
    return cf.faasm_get_state(key, len)


def get_state_offset(key, total_len, offset, offset_len):
    return cf.faasm_get_state_offset(key, total_len, offset, offset_len)


def set_state(key, value):
    cf.faasm_set_state(key, value)


def set_state_offset(key, total_len, offset, value):
    cf.faasm_set_state_offset(key, total_len, offset, value)


def push_state(key):
    cf.faasm_push_state(key)


def push_state_partial(key):
    cf.faasm_push_state_partial(key)


def pull_state(key, state_len):
    cf.faasm_pull_state(key, state_len)


def chain_this_with_input(func, chained_input_data):
    if PYTHON_LOCAL_CHAINING:
        # Run function directly
        func(chained_input_data)
        return 0
    else:
        # Call native
        func_name = func.__name__
        return cf.faasm_chain_py(func_name, chained_input_data)


def await_call(call_id):
    if PYTHON_LOCAL_CHAINING:
        # Calls are run immediately
        return 0
    else:
        # Call native
        return cf.faasm_await_call(call_id)


def set_emulator_message(message_json):
    if PYTHON_LOCAL_OUTPUT:
        global output_data
        output_data = None

    return cf.set_emulator_message(message_json)


def set_emulator_status(success):
    cf.set_emulator_status(success)


def get_emulator_async_response():
    return cf.get_emulator_async_response()
