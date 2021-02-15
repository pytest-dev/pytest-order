_pytest-order_ - a pytest plugin to order test execution
========================================================

[![PyPI version](https://badge.fury.io/py/pytest-order.svg)](https://pypi.org/project/pytest-order) [![Testsuite](https://github.com/mrbean-bremen/pytest-order/workflows/Testsuite/badge.svg)](https://github.com/mrbean-bremen/pytest-order/actions?query=workflow%3ATestsuite) [![DocBuild](https://github.com/mrbean-bremen/pytest-order/workflows/DocBuild/badge.svg)](https://github.com/mrbean-bremen/pytest-order/actions?query=workflow%3ADocBuild) [![codecov](https://codecov.io/gh/mrbean-bremen/pytest-order/branch/master/graph/badge.svg?token=M9PHWZSHUU)](https://codecov.io/gh/mrbean-bremen/pytest-order) [![Python version](https://img.shields.io/pypi/pyversions/pytest-order.svg)](https://pypi.org/project/pytest-order)

`pytest-order` is a pytest plugin that allows you to customize the order in which
your tests are run. It uses the marker `order` that defines when a specific
test shall be run relative to the other tests. 

`pytest-order` is a fork of
[pytest-ordering](https://github.com/ftobia/pytest-ordering) that provides
some additional features - see [below](#comparison-with-pytest_ordering) for
details.

`pytest-order` works with Python 2.7 and 3.5 - 3.9, with pytest 
versions >= 3.7.0, and runs on Linux, MacOs and Windows.

Documentation
-------------
Apart from this overview, the following information is available:
- usage documentation for the [latest release](https://mrbean-bremen.github.io/pytest-order/stable/)
- usage documentation for the [current master](https://mrbean-bremen.github.io/pytest-order/dev/)
- all examples shown in the documentation can also be found in the 
  [repository](https://github.com/mrbean-bremen/pytest-order/tree/master/example)
- the [Release Notes](https://github.com/mrbean-bremen/pytest-order/blob/master/CHANGELOG.md)
  with a list of changes in the latest versions
- a [list of open issues](https://github.com/mrbean-bremen/pytest-order/blob/master/old_issues.md)
  in the original project and their handling in `pytest-order`

Overview
--------
_(adapted from the original project)_

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

    $ pytest test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 2 items

    test_foo.py:7: test_bar PASSED
    test_foo.py:3: test_foo PASSED

    =========================== 2 passed in 0.01 seconds ===========================

Features
--------
`pytest-order` provides the following features:
- ordering of tests by index, as shown above
- ordering of tests both from the start and from the end (via negative
  index)
- ordering of tests relative to each other (via the `before` and `after`
  marker attributes) 
- session-, module- and class-scope ordering via the ``order-scope`` option
- hierarchical ordering via the ``group-order-scope`` option
- ordering tests with `pytest-dependency` markers if using the
  ``order-dependencies`` option
- sparse ordering of tests via the ``sparse-ordering`` option
- invocation of the plugin before other plugins if the
  ``indulgent-ordering`` option is used
  
A usage guide for each feature can be
found in the [documentation](https://mrbean-bremen.github.io/pytest-order/dev/).

History
-------
This is a fork of [pytest-ordering](https://github.com/ftobia/pytest-ordering).
That project is not maintained anymore, and there are several helpful PRs
that are now integrated into `pytest-order`. The idea and most of the code
has been created by Frank Tobia, the author of that plugin, and
[contributors](https://github.com/mrbean-bremen/pytest-order/blob/master/AUTHORS).

Comparison with pytest_ordering
-------------------------------
While derived from `pytest_ordering`, `pytest-order` is **not** compatible
with `pytest-ordering` due to the changed marker name (`order` instead of
`run`). Additional markers are integrated into the `order` marker (for a 
rationale see also
[this issue](https://github.com/ftobia/pytest-ordering/issues/38)).

Ordering relative to other tests and all of the configuration options are not
available in the released version of `pytest-ordering`.
However, most of these features are derived from 
[issues](https://github.com/mrbean-bremen/pytest-order/blob/master/old_issues.md)
and pull requests already existing in `pytest-ordering`. 
