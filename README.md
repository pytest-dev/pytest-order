_pytest-order_ - a pytest plugin to order test execution
========================================================

[![PyPI version](https://badge.fury.io/py/pytest-order.svg)](https://pypi.org/project/pytest-order) [![Testsuite](https://github.com/pytest-dev/pytest-order/workflows/Testsuite/badge.svg)](https://github.com/pytest-dev/pytest-order/actions?query=workflow%3ATestsuite) [![DocBuild](https://github.com/pytest-dev/pytest-order/workflows/DocBuild/badge.svg)](https://github.com/pytest-dev/pytest-order/actions?query=workflow%3ADocBuild) [![codecov](https://codecov.io/gh/pytest-dev/pytest-order/branch/main/graph/badge.svg?token=M9PHWZSHUU)](https://codecov.io/gh/pytest-dev/pytest-order) [![Python version](https://img.shields.io/pypi/pyversions/pytest-order.svg)](https://pypi.org/project/pytest-order)

`pytest-order` is a pytest plugin that allows you to customize the order in which
your tests are run. It uses the marker `order` that defines when a specific
test shall run, either by using an ordinal number, or by specifying the  
relationship to other tests. 

`pytest-order` is a fork of
[pytest-ordering](https://github.com/ftobia/pytest-ordering) that provides
additional features like ordering relative to other tests.

`pytest-order` works with Python 3.6 - 3.10, with pytest 
versions >= 5.0.0 for all versions except Python 3.10, and for pytest >=
6.2.4 for Python 3.10. `pytest-order` runs on Linux, macOS and Windows.

Documentation
-------------
Apart from this overview, the following information is available:
- usage documentation for the [latest release](https://pytest-dev.github.io/pytest-order/stable/)
- usage documentation for the [current main branch](https://pytest-dev.github.io/pytest-order/dev/)
- most examples shown in the documentation can also be found in the 
  [repository](https://github.com/pytest-dev/pytest-order/tree/main/example)
- the [Release Notes](https://github.com/pytest-dev/pytest-order/blob/main/CHANGELOG.md)
  with a list of changes in the latest versions
- a [list of open issues](https://github.com/pytest-dev/pytest-order/blob/main/old_issues.md)
  in the original project and their handling in `pytest-order`

Features
--------
`pytest-order` provides the following features:
- ordering of tests [by index](https://pytest-dev.github.io/pytest-order/stable/usage.html#ordering-by-numbers)
- ordering of tests both from the start and from the end (via negative
  index)
- ordering of tests [relative to each other](https://pytest-dev.github.io/pytest-order/stable/usage.html#order-relative-to-other-tests)
  (via the `before` and `after` marker attributes)
- session-, module- and class-scope ordering via the
  [order-scope](https://pytest-dev.github.io/pytest-order/stable/configuration.html#order-scope) option
- directory scope ordering via the
  [order-scope-level](https://pytest-dev.github.io/pytest-order/stable/configuration.html#order-scope-level) option
- hierarchical module and class-level ordering via the 
  [order-group-scope](https://pytest-dev.github.io/pytest-order/stable/configuration.html#order-group-scope) option
- ordering tests with `pytest-dependency` markers if using the
  [order-dependencies](https://pytest-dev.github.io/pytest-order/stable/configuration.html#order-dependencies) option, 
  more information about `pytest-dependency` compatibility
  [here](https://pytest-dev.github.io/pytest-order/stable/other_plugins.html#relationship-with-pytest-dependency) 
- sparse ordering of tests via the 
  [sparse-ordering](https://pytest-dev.github.io/pytest-order/stable/configuration.html#sparse-ordering) option

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

Contributing
------------
Contributions are very welcome. Tests can be run with 
[tox](https://tox.readthedocs.io/en/latest/), please ensure
the coverage at least stays the same before you submit a pull request.

License
-------
Distributed under the terms of the [MIT](http://opensource.org/licenses/MIT)
license, `pytest-order` is free and open source software.

History
-------
This is a fork of [pytest-ordering](https://github.com/ftobia/pytest-ordering).
That project is not maintained anymore, and there are several helpful PRs
that are now integrated into `pytest-order`. The idea and most of the 
initial code has been created by Frank Tobia, the author of that plugin, and
[contributors](https://github.com/pytest-dev/pytest-order/blob/main/AUTHORS).

While derived from `pytest_ordering`, `pytest-order` is **not** compatible
with `pytest-ordering` due to the changed marker name (`order` instead of
`run`). Additional markers defined `pytest_ordering` are all integrated 
into the `order` marker (for a rationale see also
[this issue](https://github.com/ftobia/pytest-ordering/issues/38)).

Ordering relative to other tests and all the configuration options are not
available in the released version of `pytest-ordering`.
However, most of these features are derived from or inspired by  
[issues](https://github.com/pytest-dev/pytest-order/blob/main/old_issues.md)
and pull requests already existing in `pytest-ordering`.
