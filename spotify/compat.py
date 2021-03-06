import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no branch
    from collections import Iterable, MutableSequence, Sequence  # noqa

    text_type = unicode  # noqa
    binary_type = str
else:
    from collections.abc import Iterable, MutableSequence, Sequence  # noqa

    text_type = str
    binary_type = bytes
