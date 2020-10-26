pytest-order [![PyPI version](https://badge.fury.io/py/pytest-order.svg)](https://badge.fury.io/py/pytest-order) [![Build Status](https://travis-ci.org/mrbean-bremen/pytest-order.svg?branch=master)](https://travis-ci.org/mrbean-bremen/pytest-order) [![Python version](https://img.shields.io/pypi/pyversions/pytest-order.svg)](https://img.shields.io/pypi/pyversions/pytest-order.svg)
============
`pytest-order` is a pytest plugin that allows you to customize the order in which
your tests are run. It uses the marker `order` that defines when a specific
test shall be run relative to the other tests.  

This is a fork of [pytest-ordering](https://github.com/ftobia/pytest-ordering).
That project is not maintained anymore, and there are several helpful PRs
that are now integrated into `pytest-order`. The idea and most of the code
has been created by Frank Tobia, the author of that plugin. In case 
`pytest-ordering` is revived, this project will be obsolete. 

_Note:_ `pytest-order` is not compatible with `pytest-ordering` due to the
changed marker name (`order` instead of `run`). Only the `order` 
marker is supported, support for all additional markers has been removed for
consistence (see [this issue](https://github.com/ftobia/pytest-ordering/issues/38)).

More information can be found in the documentation:
- for the [latest release](https://mrbean-bremen.github.io/pytest-order/stable/)
- for the [current master](https://mrbean-bremen.github.io/pytest-order/dev/)

_From the original project:_

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

    @pytest.mark.run(order=2)
    def test_foo():
        assert True

    @pytest.mark.run(order=1)
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
