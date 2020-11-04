# -*- coding: utf-8 -*-

import pytest

import pytest_order


def test_run_marker_registered(capsys, tmpdir):
    testname = str(tmpdir.join("failing.py"))
    with open(testname, "w") as fi:
        fi.write(
            """
import pytest

@pytest.mark.order("second")
def test_me_second():
    assert True

def test_that_fails():
    assert False

@pytest.mark.order("first")
def test_me_first():
    assert True
"""
        )
    args = ["--quiet", "--color=no", testname]
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    assert "..F" in out
    args.insert(0, "--ff")
    # pytest 6 seems to have changed the order plugins are executed
    if int(pytest.__version__[:pytest.__version__.index(".")]) < 6:
        pytest.main(args, [pytest_order])
        out, err = capsys.readouterr()
        assert "..F" in out
    args.insert(0, "--indulgent-ordering")
    pytest.main(args, [pytest_order])
    out, err = capsys.readouterr()
    assert "F.." in out
