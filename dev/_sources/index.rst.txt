Introduction
============
``pytest-order`` is a pytest plugin which allows you to customize the order
in which run your tests are run. It provides the marker ``order``, that has
attributes that defines when your tests should run in relation to each other.
These attributes can be absolute (i.e. first, or second-to-last) or relative
(i.e. run this test before this other test).

Relationship with pytest-ordering
---------------------------------
``pytest-order`` is a fork of
`pytest-ordering <https://github.com/ftobia/pytest-ordering>`__, which is
not maintained anymore. The idea and most of the code has been created by
Frank Tobia, the author of that plugin.

However, ``pytest-order`` is not compatible with ``pytest-ordering`` due to the
changed marker name (``order`` instead of ``run``) and the removal of all
other special markers for consistence (see
`this issue <https://github.com/ftobia/pytest-ordering/issues/38>`__). This
also avoids clashes between the plugins if they are both installed.

Here are examples for which markers correspond to markers in
``pytest-ordering``:

- ``pytest.mark.order1``, ``pytest.mark.run(order=1)`` => ``pytest.mark.order(1)``
- ``pytest.mark.first`` => ``pytest.mark.order("first")``


Supported Python and pytest versions
------------------------------------
pytest-order supports python 2.7, 3.5 - 3.8, and pypy, and is
compatible with pytest 3.6.0 or newer. Note that support for Python 2 will
be removed in one of the next versions.

Installation
------------
The latest released version can be installed from
`PyPi <https://pypi.python.org/pypi/pytest-order/>`__:

.. code:: bash

   pip install pytest-order

The latest master can be installed from the GitHub sources:

.. code:: bash

   pip install git+https://github.com/mrbean-bremen/pytest-order

Overview
--------
Ordinarily pytest will run tests in the order that they appear in a module.
For example, for the following tests:

.. code:: python

 def test_foo():
     assert True

 def test_bar():
     assert True

Here is the output:

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    collected 2 items

    test_foo.py:2: test_foo PASSED
    test_foo.py:6: test_bar PASSED

    =========================== 2 passed in 0.01 seconds ===========================

With pytest-order, you can change the default ordering as follows:

.. code:: python

 import pytest

 @pytest.mark.order(2)
 def test_foo():
     assert True

 @pytest.mark.order(1)
 def test_bar():
     assert True

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 2 items

    test_foo.py:7: test_bar PASSED
    test_foo.py:3: test_foo PASSED

    =========================== 2 passed in 0.01 seconds ===========================

Usage
=====
The above is a trivial example, but ordering is respected across test files.
There are currently three possibilities to define the order:

Order by number
---------------
As already shown above, the order can be defined using ordinal numbers.
Negative numbers are also allowed - they are used the same way as indexes
are used in Python lists, e.g. to count from the end:

.. code:: python

 import pytest

 @pytest.mark.order(-2)
 def test_three():
     assert True

 @pytest.mark.order(-1)
 def test_four():
     assert True

 @pytest.mark.order(2)
 def test_two():
     assert True

 @pytest.mark.order(1)
 def test_one():
     assert True

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 4 items

    test_foo.py:17: test_one PASSED
    test_foo.py:12: test_two PASSED
    test_foo.py:3: test_three PASSED
    test_foo.py:7: test_four PASSED

    =========================== 4 passed in 0.02 seconds ===========================

There is no limit for the numbers that can be used in this way.

Order using ordinals
--------------------

You can also use markers such as "first", "second", "last", and
"second_to_last". These are convenience notations, and have the same effect
as the numbers 0, 1, -1 and -2 that have been shown above:

.. code:: python

 import pytest

 @pytest.mark.order('second_to_last')
 def test_three():
     assert True

 @pytest.mark.order('last')
 def test_four():
     assert True

 @pytest.mark.order('second')
 def test_two():
     assert True

 @pytest.mark.order('first')
 def test_one():
     assert True

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 4 items

    test_foo.py:17: test_one PASSED
    test_foo.py:12: test_two PASSED
    test_foo.py:3: test_three PASSED
    test_foo.py:7: test_four PASSED

    =========================== 4 passed in 0.02 seconds ===========================

Convenience names are only defined for the first and the last 8 numbers, 
here is the complete list with the corresponding numbers:

- 'first': 0
- 'second': 1
- 'third': 2
- 'fourth': 3
- 'fifth': 4
- 'sixth': 5
- 'seventh': 6
- 'eighth': 7
- 'last': -1
- 'second_to_last': -2
- 'third_to_last': -3
- 'fourth_to_last': -4
- 'fifth_to_last': -5
- 'sixth_to_last': -6
- 'seventh_to_last': -7
- 'eighth_to_last': -8

Order relative to other tests
-----------------------------
The test order can be defined relative to other tests, which are referenced
by their name:

.. code:: python

 import pytest

 @pytest.mark.order(after='test_second')
 def test_third():
     assert True

 def test_second():
     assert True

 @pytest.mark.run(before='test_second')
 def test_first():
     assert True

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 3 items

    test_foo.py:11: test_first PASSED
    test_foo.py:7: test_second PASSED
    test_foo.py:4: test_third PASSED

    =========================== 4 passed in 0.02 seconds ===========================

Configuration
=============
Currently there is only one option that changes the behavior of the plugin.

``--indulgent-ordering`` and overriding ordering
------------------------------------------------
You may sometimes find that you want to suggest an ordering of tests, while
allowing it to be overridden for good reason. For example, if you run your test
suite in parallel and have a number of tests which are particularly slow, it
might be desirable to start those tests running first, in order to optimize
your completion time. You can use the pytest-order plugin to inform pytest
of this.
Now suppose you also want to prioritize tests which failed during the
previous run, by using the ``--failed-first`` option. By default,
pytest-order will override the ``--failed-first`` order, but by adding the
``--indulgent-ordering`` option, you can ask pytest to run the sort from
pytest-order *before* the sort from ``--failed-first``, allowing the failed
tests to be sorted to the front.


.. toctree::
   :maxdepth: 2

.. _markers: https://pytest.org/latest/mark.html

