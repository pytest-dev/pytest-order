import re


def write_test(path, contents):
    with open(path, "w") as fi:
        fi.write(contents)


def assert_test_order(test_names, out):
    expected = ".*" + ".*".join(test_names)
    assert re.match(expected, out.replace("\n", "")), out
