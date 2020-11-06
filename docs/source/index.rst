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
  problems or legacy code. Still, before using this plugin, you should check
  if you can refactor your tests to remove the dependencies between tests.

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


Supported Python and pytest versions
------------------------------------
``pytest-order`` supports python 2.7, 3.5 - 3.9, and pypy/pypy3, and is
compatible with pytest 3.6.0 or newer. Note that support for Python 2 will
be removed in one of the next versions.

All supported combinations of Python and pytest versions are tested in
the CI builds. The plugin shall work under Linux, MacOs and Windows.

Installation
------------
The latest released version can be installed from
`PyPi <https://pypi.python.org/pypi/pytest-order/>`__:

.. code:: bash

   pip install pytest-order

The latest master can be installed from the GitHub sources:

.. code:: bash

   pip install git+https://github.com/mrbean-bremen/pytest-order

Quickstart
----------
Ordinarily pytest will run tests in the order that they appear in a module.
For example, for the following tests:

.. code:: python

 def test_foo():
     assert True

 def test_bar():
     assert True

the output is something like:

::

    $ py.test test_foo.py -vv
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

This will generate the output:

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

.. note::
  The scope of the ordering is global per default, e.g. tests with lower
  ordinal numbers are always executed before tests with higher numbers,
  regardless of the module and class they reside in. This can be changed
  by using the :ref:`order-scope` option.

There are currently three possibilities to define the order:

Order by number
---------------
As already shown above, the order can be defined using ordinal numbers.
Negative numbers are also allowed--they are used the same way as indexes
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

Instead of the numbers, you can use ordinal names such as "first", "second",
"last", and "second_to_last". These are convenience notations, and have the
same effect as the numbers 0, 1, -1 and -2 that have been shown above:

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

Convenience names are only defined for the first and the last 8 numbers.
Here is the complete list with the corresponding numbers:

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

If a test is referenced using the unqualified test name as shown in the
example, the test is assumed to be in the current module. For tests in other
modules the qualified test name (e.g. ``my_module.test_something``) has to
be used.

If an unknown test is referenced, a warning is issued and the test in
question is ordered behind all other tests.

.. note::
  The `pytest-dependency <https://pypi.org/project/pytest-dependency/>`__
  plugin also manages dependencies between tests (skips tests that depend
  on skipped or failed tests), but doesn't do any ordering. You can combine
  both plugins if you need both options.

Configuration
=============
There are a few command line options that change the behavior of the
plugin. As with any pytest option, you can add the options to your
``pytest.ini`` if you want to have them applied to all tests automatically.

``--indulgent-ordering``
------------------------
You may sometimes find that you want to suggest an ordering of tests, while
allowing it to be overridden for good reason. For example, if you run your test
suite in parallel and have a number of tests which are particularly slow, it
might be desirable to start those tests running first, in order to optimize
your completion time. You can use the ``pytest-order`` plugin to inform pytest
of this.

Now suppose you also want to prioritize tests which failed during the
previous run, by using the ``--failed-first`` option. By default,
pytest-order will override the ``--failed-first`` order, but by adding the
``--indulgent-ordering`` option, you can ask pytest to run the sort from
pytest-order *before* the sort from ``--failed-first``, allowing the failed
tests to be sorted to the front (note that in pytest versions from 6.0 on,
this seems not to be needed anymore, at least in this specific case).

.. _order-scope:

``--order-scope``
-----------------
By default, tests are ordered per session, e.g. across all modules in the
test run. Sometimes, you want to order tests per module or per test class
instead. Consider that you have a growing number of test modules that you
want to run simultaneously, with tests ordered per module. Per default you
would need to make sure that the order numbers increases globally, if you
want to run the test modules consecutively and order the test per module.

If you use the option ``--order-scope=module``, there is no need for this.
You can enumerate your tests starting with 0 or 1 in each module, and the tests
will only be ordered inside each module. Using ``--order-scope=class``
additionally considers test classes--each test class is considered
separately for ordering the tests. If a module has both test classes and
separate test functions, these test functions are handled separately from the
test classes. If a module has no test classes, the effect is the same as
if using ``--order-scope=module``.

``--sparse-ordering``
---------------------
Ordering tests by ordinals where some numbers are missing by default behaves
the same as if the the ordinals are consecutive. For example, these tests:

.. code:: python

 import pytest

 @pytest.mark.order(3)
 def test_two():
     assert True

 def test_three():
     assert True

 def test_four():
     assert True

 @pytest.mark.order(1)
 def test_one():
     assert True

are executed in the same order as:

.. code:: python

 import pytest

 @pytest.mark.order(1)
 def test_two():
     assert True

 def test_three():
     assert True

 def test_four():
     assert True

 @pytest.mark.order(0)
 def test_one():
     assert True

namely, they are run in the order ``test_one``, ``test_two``, ``test_three``
and ``test_four``. The gaps between numbers, and the fact that the starting
number is not 0, are ignored. This is consistent with the current behavior of
``pytest-ordering``.

If you use the ``--sparse-ordering`` option, the behavior will change: now
all missing numbers (starting with 0) are filled with unordered tests, as
long as unordered tests are left. So the shown example will now order as
``test_three`` (filled in for the missing number 0), ``test_one``,
``test_four`` (filled in for the missing number 2), and ``test_two``. This
will also work for tests with negative order numbers (or the respective names).
The missing ordinals are filled with unordered tests first from the start,
then from the end if there are negative numbers, and the rest will be in
between (e.g. between positive and negative numbers), as it is without this
option.


Miscellaneous
=============

Usage with pytest-xdist
-----------------------
The ``pytest-xdist`` plugin schedules tests unordered, and the order
configured by ``pytest-order`` will normally not be preserved. But
if we use the ``--dist=loadfile`` option, provided by ``xdist``, all tests
from one file will be run in the same thread. So, to make the two plugins work
together, we have to put each group of dependent tests in one file, and call
pytest with ``--dist=loadfile`` (this is taken from
`this issue <https://github.com/ftobia/pytest-ordering/issues/36>`__).

.. toctree::
   :maxdepth: 2

.. _markers: https://pytest.org/latest/mark.html
