.. pytest-ordering documentation master file, created by
   sphinx-quickstart on Mon Mar 17 18:20:44 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pytest-ordering2: run your tests in  order
==========================================

pytest-ordering2 is a pytest plugin to run your tests in any order that
you specify. It provides custom markers_ that say when your tests should
run in relation to each other. They can be absolute (i.e. first, or
second-to-last) or relative (i.e. run this test before this other test).

Supported Python and pytest versions
------------------------------------

pytest-ordering2 supports python 2.7, 3.5 - 3.8, and pypy, and is
compatible with pytest 3.6.0 or newer.


Quickstart
----------

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
    platform darwin -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2 -- env/bin/python
    collected 2 items

    test_foo.py:2: test_foo PASSED
    test_foo.py:6: test_bar PASSED

    =========================== 2 passed in 0.01 seconds ===========================

With pytest-ordering, you can change the default ordering as follows:

.. code:: python

 import pytest

 @pytest.mark.run(order=2)
 def test_foo():
     assert True

 @pytest.mark..run(order=1)
 def test_bar():
     assert True

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2 -- env/bin/python
    plugins: ordering
    collected 2 items

    test_foo.py:7: test_bar PASSED
    test_foo.py:3: test_foo PASSED

    =========================== 2 passed in 0.01 seconds ===========================

This is a trivial example, but ordering is respected across test files.
There are several possibilities to define the order.

By number
---------
As already shown above, the order can be defined using ordinal numbers.
Negative numbers are also allowed - they are used the same way as indexes
used in Python lists, e.g. to count from the end:

.. code:: python

 import pytest

 @pytest.mark.run(order=-2)
 def test_three():
     assert True

 @pytest.mark.run(order=-1)
 def test_four():
     assert True

 @pytest.mark.run(order=2)
 def test_two():
     assert True

 @pytest.mark.run(order=1)
 def test_one():
     assert True

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2 -- env/bin/python
    plugins: ordering
    collected 4 items

    test_foo.py:17: test_one PASSED
    test_foo.py:12: test_two PASSED
    test_foo.py:3: test_three PASSED
    test_foo.py:7: test_four PASSED

    =========================== 4 passed in 0.02 seconds ===========================


Ordinals
--------

You can also use markers such as "first", "second", "last", and
"second_to_last". These are convenience notations, and have the same effect
as the numbers 1, 2, -1 and -2 that have been shown above:

.. code:: python

 import pytest

 @pytest.mark.second_to_last
 def test_three():
     assert True

 @pytest.mark.last
 def test_four():
     assert True

 @pytest.mark.second
 def test_two():
     assert True

 @pytest.mark.first
 def test_one():
     assert True

::

    $ py.test test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2 -- env/bin/python
    plugins: ordering
    collected 4 items

    test_foo.py:17: test_one PASSED
    test_foo.py:12: test_two PASSED
    test_foo.py:3: test_three PASSED
    test_foo.py:7: test_four PASSED

    =========================== 4 passed in 0.02 seconds ===========================

Relative to other tests
-----------------------

The test order can be defined relative to other tests, which are referenced
by their name:

.. code:: python

 import pytest

 @pytest.mark.run(after='test_second')
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
    platform darwin -- Python 2.7.5 -- py-1.4.20 -- pytest-2.5.2 -- env/bin/python
    plugins: ordering
    collected 3 items

    test_foo.py:11: test_first PASSED
    test_foo.py:7: test_second PASSED
    test_foo.py:4: test_third PASSED

    =========================== 4 passed in 0.02 seconds ===========================

``--indulgent-ordering`` and overriding ordering
------------------------------------------------

You may sometimes find that you want to suggest an ordering of tests, while
allowing it to be overridden for good reason. For example, if you run your test
suite in parallel and have a number of tests which are particularly slow, it
might be desirable to start those tests running first, in order to optimize
your completion time. You can use the pytest-ordering2 plugin to inform pytest
of this.
Now suppose you also want to prioritize tests which failed during the
previous run, by using the ``--failed-first`` option. By default,
pytest-ordering will override the ``--failed-first`` order, but by adding the
``--indulgent-ordering`` option, you can ask pytest to run the sort from
pytest-ordering2 *before* the sort from ``--failed-first``, allowing the failed
tests to be sorted to the front.



.. toctree::
   :maxdepth: 2

.. _markers: https://pytest.org/latest/mark.html

