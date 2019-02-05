import sys


PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no branch
    text_type = unicode  # noqa
    binary_type = str
else:
    text_type = str
    binary_type = bytes
