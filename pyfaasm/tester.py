from pyfaasm.core import check_python_bindings
from pyfaasm.core import get_state, get_state_offset, set_state, set_state_offset, push_state, pull_state

# Initial check
check_python_bindings()

# Write and push state
key = "pyStateTest"
valueLen = 10
fullValue = b'0123456789'
set_state(key, fullValue)
push_state(key)

# Read state back in
pull_state(key, valueLen)
actual = get_state(key, valueLen)
print("In = {}  out = {}".format(fullValue, actual))

# Update a segment
segment = b'999'
offset = 2
segmentLen = 3
modifiedValue = b'0199956789'
set_state_offset(key, valueLen, offset, segment)
push_state(key)

pull_state(key, valueLen)
actual = get_state(key, valueLen)
actualSegment = get_state_offset(key, valueLen, offset, segmentLen)
print("Expected = {}  actual = {}".format(modifiedValue, actual))
print("Expected = {}  actual = {}".format(segment, actualSegment))
