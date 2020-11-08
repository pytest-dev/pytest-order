_pytest-order_ - a pytest plugin to order test execution
========================================================

[![PyPI version](https://badge.fury.io/py/pytest-order.svg)](https://pypi.org/project/pytest-order) ![Testsuite](https://github.com/mrbean-bremen/pytest-order/workflows/Testsuite/badge.svg) ![DocBuild](https://github.com/mrbean-bremen/pytest-order/workflows/DocBuild/badge.svg) [![Coverage Status](https://img.shields.io/coveralls/github/mrbean-bremen/pytest-order)](https://coveralls.io/github/mrbean-bremen/pytest-order) [![Python version](https://img.shields.io/pypi/pyversions/pytest-order.svg)](https://pypi.org/project/pytest-order)

`pytest-order` is a pytest plugin that allows you to customize the order in which
your tests are run. It uses the marker `order` that defines when a specific
test shall be run relative to the other tests.  

`pytest-order` works with Python 2.7 and 3.5 - 3.9, with pytest 
versions >= 3.7.0, and runs on Linux, MacOs and Windows.


Documentation
-------------
Apart from this overview, the following information is available:
- usage documentation for the [latest release](https://mrbean-bremen.github.io/pytest-order/stable/)
- usage documentation for the [current master](https://mrbean-bremen.github.io/pytest-order/dev/)
- the [Release Notes](https://github.com/mrbean-bremen/pytest-order/blob/master/CHANGELOG.md)
  with a list of changes in the latest versions

History
-------
This is a fork of [pytest-ordering](https://github.com/ftobia/pytest-ordering).
That project is not maintained anymore, and there are several helpful PRs
that are now integrated into `pytest-order`. The idea and most of the code
has been created by Frank Tobia, the author of that plugin, and
[contributors](https://github.com/mrbean-bremen/pytest-order/blob/master/AUTHORS).

Compatibility with pytest_ordering
----------------------------------
`pytest-order` is **not** compatible with `pytest-ordering` due to the
changed marker name (`order` instead of `run`). Only the `order` 
marker is supported, support for all additional markers has been removed for
consistence (as has been discussed in 
[this issue](https://github.com/ftobia/pytest-ordering/issues/38)).

Overview
--------
_(from the original project)_

Have you ever wanted to easily run one of your tests before any others run?
Or run some tests last? Or run this one test before that other test? Or
make sure that this group of tests runs after this other group of tests?

Now you can.

Install with:

    pip install pytest-order

This defines the ``order`` marker that you can use in your code with
different attributes. 

For example, this code:

    import pytest

    @pytest.mark.order(2)
    def test_foo():
        assert True

    @pytest.mark.order(1)
    def test_bar():
        assert True

yields the output:

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 2 items

    test_foo.py:7: test_bar PASSED
    test_foo.py:3: test_foo PASSED

    =========================== 2 passed in 0.01 seconds ===========================
