from pyfaasm.core import (
    read_state,
    read_state_offset,
    init_host_interface,
    write_state,
    write_state_offset,
    push_state,
    pull_state,
    set_emulator_message,
)
import json

init_host_interface()

msg = {
    "user": "demo",
    "function": "echo",
}
set_emulator_message(json.dumps(msg))

# Write and push state
key = "pyStateTest"
valueLen = 10
fullValue = b"0123456789"
write_state(key, fullValue)
push_state(key)

# Read state back in
pull_state(key, valueLen)
actual = read_state(key, valueLen)
print("In = {}  out = {}".format(fullValue, actual))

# Update a segment
segment = b"999"
offset = 2
segmentLen = 3
modifiedValue = b"0199956789"
write_state_offset(key, valueLen, offset, segment)
push_state(key)

pull_state(key, valueLen)
actual = read_state(key, valueLen)
actualSegment = read_state_offset(key, valueLen, offset, segmentLen)
print("Expected = {}  actual = {}".format(modifiedValue, actual))
print("Expected = {}  actual = {}".format(segment, actualSegment))
