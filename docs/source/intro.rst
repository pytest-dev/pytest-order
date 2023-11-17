Introduction
============
``pytest-order`` is a pytest plugin which allows you to customize the order
in which your tests are run. It provides the marker ``order``, that has
attributes that define when your tests should run in relation to each other.
These attributes can be absolute (i.e. first, or second-to-last) or relative
(i.e. run this test before this other test).

.. note::
  It is generally considered bad practice to write tests that depend on each
  other. However, in reality this may still be needed due to performance
  issues, legacy code or other constraints. Still, before using this plugin,
  you should check if you can refactor your tests to remove the dependencies
  between tests.

Relationship with pytest-ordering
---------------------------------
``pytest-order`` is a fork of
`pytest-ordering <https://github.com/ftobia/pytest-ordering>`__, which is
not maintained anymore. The idea and most of the code has been created by
Frank Tobia, the author of that plugin, and contributors to the project.

However, ``pytest-order`` is not compatible with ``pytest-ordering`` due to the
changed marker name (``order`` instead of ``run``) and the removal of all
other special markers for consistence (as has been discussed in
`this issue <https://github.com/ftobia/pytest-ordering/issues/38>`__). This
also avoids clashes between the plugins if they are both installed.

Here are examples for which markers correspond to markers in
``pytest-ordering``:

- ``pytest.mark.order1``, ``pytest.mark.run(order=1)`` => ``pytest.mark.order(1)``
- ``pytest.mark.first`` => ``pytest.mark.order("first")``

Additionally, ``pytest-order`` provides a number of features (relative
ordering, all configuration options) that are not available in
``pytest-ordering``.

Supported Python and pytest versions
------------------------------------
``pytest-order`` supports python 3.7 - 3.12 and pypy3, and is
compatible with pytest 5.0.0 or newer (older versions may also work, but are
not tested) for Python versions up to 3.9, and with pytest >= 6.2.4 for
Python versions >= 3.10.

All supported combinations of Python and pytest versions are tested in
the CI builds. The plugin shall work under Linux, MacOs and Windows.

Installation
------------
The latest released version can be installed from
`PyPi <https://pypi.python.org/pypi/pytest-order/>`__:

.. code:: bash

   pip install pytest-order

The latest main branch can be installed from the GitHub sources:

.. code:: bash

   pip install git+https://github.com/pytest-dev/pytest-order

Examples
--------
Most examples shown in this documentation can be also found in the repository
under `example <https://github.com/pytest-dev/pytest-order/tree/main/example/>`__
as working test files.

Quickstart
----------
Ordinarily pytest will run tests in the order that they appear in a module.
For example, for the following tests:

.. code:: python

 def test_foo():
     assert True


 def test_bar():
     assert True

the output is something like::

    $ pytest test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    collected 2 items

    test_foo.py:2: test_foo PASSED
    test_foo.py:6: test_bar PASSED

    =========================== 2 passed in 0.01 seconds ===========================

With ``pytest-order``, you can change the default ordering as follows:

.. code:: python

 import pytest


 @pytest.mark.order(2)
 def test_foo():
     assert True


 @pytest.mark.order(1)
 def test_bar():
     assert True

This will generate the output::

    $ pytest test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 2 items

    test_foo.py:7: test_bar PASSED
    test_foo.py:3: test_foo PASSED

    =========================== 2 passed in 0.01 seconds ===========================
