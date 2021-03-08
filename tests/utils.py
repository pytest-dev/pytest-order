import os
import re


def write_test(path, contents):
    parent = os.path.split(path)[0]
    if not os.path.exists(parent):
        os.makedirs(parent)
    with open(path, "w") as fi:
        fi.write(contents)


def assert_test_order(test_names, out):
    expected = ".*" + ".*".join(test_names)
    assert re.match(expected, out.replace("\n", "")), out
