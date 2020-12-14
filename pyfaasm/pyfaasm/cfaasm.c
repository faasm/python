#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Must make sure resulting wasm imports the Faasm interface funcs
#define FAASM_IMPORT extern

// Some useful notes
// - Tutorial - https://realpython.com/build-python-c-extension-module/
// - Official tutorial - https://docs.python.org/3/extending/extending.html
// - Numpy example - https://dfm.io/posts/python-c-extensions/
// - Args and return values - https://docs.python.org/3/c-api/arg.html
// - Bytes objects - https://docs.python.org/3/c-api/bytes.html

// ------ Faasm input/output ------

FAASM_IMPORT
long __faasm_read_input(unsigned char *buffer, long bufferLen);

FAASM_IMPORT
void __faasm_write_output(const unsigned char *output, long outputLen);

// ------ Faasm state ------

FAASM_IMPORT
long __faasm_read_state(const char *key, unsigned char *buffer, long bufferLen);

FAASM_IMPORT
unsigned char *__faasm_read_state_ptr(const char *key, long totalLen);

FAASM_IMPORT
unsigned char *__faasm_read_state_offset_ptr(const char *key, long totalLen, long offset, long len);

FAASM_IMPORT
void __faasm_write_state(const char *key, const unsigned char *data, long dataLen);

FAASM_IMPORT
void __faasm_write_state_offset(const char *key, long totalLen, long offset, const unsigned char *data, long dataLen);

FAASM_IMPORT
void __faasm_push_state(const char *key);

FAASM_IMPORT
void __faasm_push_state_partial(const char *key);

FAASM_IMPORT
void __faasm_pull_state(const char *key, long stateLen);

// ------ Faasm chaining ------
FAASM_IMPORT
unsigned int __faasm_chain_py(const char* name, const unsigned char *inputData, long inputDataSize);

FAASM_IMPORT
int __faasm_await_call(unsigned int messageId);

// ------ Faasm emulator API ------
FAASM_IMPORT
unsigned int setEmulatedMessageFromJson(const char *msgJson);

FAASM_IMPORT
char* emulatorGetAsyncResponse();

FAASM_IMPORT
void emulatorSetCallStatus(int success);


// ----------------------------------
// Byte handling
// ----------------------------------
#define RETURN_BYTES(value, valueLen)                                   \
    PyObject *ret = PyBytes_FromStringAndSize((char*) value, valueLen); \
    if(!ret) return NULL;                                               \
    return ret;

// ----------------------------------
// Tester functions
// ----------------------------------

// Hello world
static PyObject *hello_faasm(PyObject *self) {
    return Py_BuildValue("s", "Hello, Faasm extension!");
}

// ----------------------------------
// Input/ output
// ----------------------------------

// Check input
static PyObject *check_input(PyObject *self) {
    unsigned char dummyInput[5];
    dummyInput[0] = '0';
    dummyInput[1] = '1';
    dummyInput[2] = '2';
    dummyInput[3] = '3';
    dummyInput[4] = '4';

    RETURN_BYTES(dummyInput, 5);
}

// Get input to the function
static PyObject *faasm_get_input(PyObject *self) {
    unsigned char emptyBuf[1];
    unsigned long inputSize = __faasm_read_input(emptyBuf, 0);

    unsigned char *inputBuf = (unsigned char *) malloc(inputSize);
    __faasm_read_input(inputBuf, inputSize);

    RETURN_BYTES(inputBuf, inputSize);
}

// Set output
static PyObject *faasm_set_output(PyObject *self, PyObject *args) {
    // Note, the type of this variable will be PyBytesObject, but the
    // Python C API just deals in generic PyObject pointers
    PyObject* outputData = NULL;
    if(!PyArg_ParseTuple(args, "S", &outputData)) {
        return NULL;
    }

    __faasm_write_output(
        (unsigned char*) PyBytes_AsString(outputData),
        PyBytes_Size(outputData)
    );

    Py_RETURN_NONE;
}

// ----------------------------------
// State
// ----------------------------------

// Get whole state size
static PyObject *faasm_get_state_size(PyObject *self, PyObject *args) {
    char* key = NULL;
    if(!PyArg_ParseTuple(args, "s", &key)) {
        return NULL;
    }

    long stateSize = __faasm_read_state(key, NULL, 0);
    return Py_BuildValue("i", stateSize);
}

// Get whole state value
static PyObject *faasm_get_state(PyObject *self, PyObject *args) {
    char* key = NULL;
    int stateLen = 0;
    if(!PyArg_ParseTuple(args, "si", &key, &stateLen)) {
        return NULL;
    }

    unsigned char *stateBuffer = __faasm_read_state_ptr(key, stateLen);
    RETURN_BYTES(stateBuffer, stateLen);
}

// Get state segment
static PyObject *faasm_get_state_offset(PyObject *self, PyObject *args) {
    char* key = NULL;
    int totalLen = 0;
    int offset = 0;
    int len = 0;
    if(!PyArg_ParseTuple(args, "siii", &key, &totalLen, &offset, &len)) {
        return NULL;
    }

    unsigned char *stateBuffer = __faasm_read_state_offset_ptr(key, totalLen, offset, len);
    RETURN_BYTES(stateBuffer, len);
}

// Set whole state value
static PyObject *faasm_set_state(PyObject *self, PyObject *args) {
    char* key = NULL;
    PyObject* value = NULL;
    if(!PyArg_ParseTuple(args, "sS", &key, &value)) {
        return NULL;
    }

    __faasm_write_state(
        key,
        (unsigned char*) PyBytes_AsString(value),
        PyBytes_Size(value)
    );

    Py_RETURN_NONE;
}

// Set state segment
static PyObject *faasm_set_state_offset(PyObject *self, PyObject *args) {
    char* key = NULL;
    int totalLen = 0;
    int offset = 0;
    PyObject * value = NULL;
    if(!PyArg_ParseTuple(args, "siiS", &key, &totalLen, &offset, &value)) {
        return NULL;
    }

    __faasm_write_state_offset(
        key,
        totalLen,
        offset,
        (unsigned char*) PyBytes_AsString(value),
        PyBytes_Size(value)
    );

    Py_RETURN_NONE;
}

// Push whole state value
static PyObject *faasm_push_state(PyObject *self, PyObject *args) {
    char* key = NULL;
    if(!PyArg_ParseTuple(args, "s", &key)) {
        return NULL;
    }

    __faasm_push_state(key);

    Py_RETURN_NONE;
}

// Push partial state value
static PyObject *faasm_push_state_partial(PyObject *self, PyObject *args) {
    char* key = NULL;
    if(!PyArg_ParseTuple(args, "s", &key)) {
        return NULL;
    }

    __faasm_push_state_partial(key);

    Py_RETURN_NONE;
}

// Pull whole state value
static PyObject *faasm_pull_state(PyObject *self, PyObject *args) {
    char* key = NULL;
    int stateLen = 0;
    if(!PyArg_ParseTuple(args, "si", &key, &stateLen)) {
        return NULL;
    }

    __faasm_pull_state(key, stateLen);

    Py_RETURN_NONE;
}

// ----------------------------------
// Chaining
// ----------------------------------

static PyObject *faasm_chain_py(PyObject *self, PyObject *args) {
    char* functionName = NULL;
    PyObject* inputData = NULL;
    if(!PyArg_ParseTuple(args, "sS", &functionName, &inputData)) {
        return NULL;
    }

    int callId = __faasm_chain_py(
        functionName,
        (unsigned char*) PyBytes_AsString(inputData),
        PyBytes_Size(inputData)
    );

    return Py_BuildValue("i", callId);
}

static PyObject *faasm_await_call(PyObject *self, PyObject *args) {
    int messageId = 0;

    if(!PyArg_ParseTuple(args, "i", &messageId)) {
        return NULL;
    }

    // Here we may be awaiting the result of a call for some time, therefore
    // we need to release the GIL and reacquire once done.
    // See https://docs.python.org/3/c-api/init.html#releasing-the-gil-from-extension-code
    int result = 0;
    Py_BEGIN_ALLOW_THREADS

    result = __faasm_await_call((unsigned int) messageId);

    Py_END_ALLOW_THREADS

    return Py_BuildValue("i", result);
}

// ----------------------------------
// Emulator
// ----------------------------------

static PyObject *set_emulator_message(PyObject *self, PyObject *args) {
    char* messageJson = NULL;
    if(!PyArg_ParseTuple(args, "s", &messageJson)) {
        return NULL;
    }

    unsigned int msgId = setEmulatedMessageFromJson(messageJson);
    return Py_BuildValue("i", msgId);
}

static PyObject *set_emulator_status(PyObject *self, PyObject *args) {
    int success = 0;
    if(!PyArg_ParseTuple(args, "i", &success)) {
        return NULL;
    }

    emulatorSetCallStatus(success);
    Py_RETURN_NONE;
}

static PyObject *get_emulator_async_response(PyObject *self) {
    char* responseStr = emulatorGetAsyncResponse();
    return Py_BuildValue("s", responseStr);
}

// ----------------------------------
// Module definition
// ----------------------------------

static PyMethodDef cfaasm_methods[] = {
        {"hello_faasm", (PyCFunction) hello_faasm, METH_NOARGS, NULL},
        {"check_input", (PyCFunction) check_input, METH_NOARGS, NULL},
        {"faasm_get_input", (PyCFunction) faasm_get_input, METH_NOARGS, NULL},
        {"faasm_set_output", (PyCFunction) faasm_set_output, METH_VARARGS, NULL},
        {"faasm_get_state", (PyCFunction) faasm_get_state, METH_VARARGS, NULL},
        {"faasm_get_state_offset", (PyCFunction) faasm_get_state_offset, METH_VARARGS, NULL},
        {"faasm_get_state_size", (PyCFunction) faasm_get_state_size, METH_VARARGS, NULL},
        {"faasm_set_state", (PyCFunction) faasm_set_state, METH_VARARGS, NULL},
        {"faasm_set_state_offset", (PyCFunction) faasm_set_state_offset, METH_VARARGS, NULL},
        {"faasm_push_state", (PyCFunction) faasm_push_state, METH_VARARGS, NULL},
        {"faasm_push_state_partial", (PyCFunction) faasm_push_state_partial, METH_VARARGS, NULL},
        {"faasm_pull_state", (PyCFunction) faasm_pull_state, METH_VARARGS, NULL},
        {"faasm_chain_py", (PyCFunction) faasm_chain_py, METH_VARARGS, NULL},
        {"faasm_await_call", (PyCFunction) faasm_await_call, METH_VARARGS, NULL},
        {"set_emulator_message", (PyCFunction) set_emulator_message, METH_VARARGS, NULL},
        {"set_emulator_status", (PyCFunction) set_emulator_status, METH_VARARGS, NULL},
        {"get_emulator_async_response", (PyCFunction) get_emulator_async_response, METH_NOARGS, NULL},
        {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cfaasmmodule = {
        PyModuleDef_HEAD_INIT,
        "cfaasm",
        "C bindings for Faasm functions",
        -1,
        cfaasm_methods
};

PyMODINIT_FUNC
PyInit_cfaasm(void) {
    return PyModule_Create(&cfaasmmodule);
}
