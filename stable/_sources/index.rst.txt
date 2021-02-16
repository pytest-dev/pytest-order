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
``pytest-order`` supports python 2.7, 3.5 - 3.9, and pypy/pypy3, and is
compatible with pytest 3.7.0 or newer. Note that support for Python 2 will
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

Examples
--------
All examples shown in this documentation can be also found in the repository
under `example <https://github.com/mrbean-bremen/pytest-order/tree/master/example/>`__
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

the output is something like:

::

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

This will generate the output:

::

    $ pytest test_foo.py -vv
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
  ordinal numbers are always executed before tests with higher numbers in
  the same test session, regardless of the module and class they reside in.
  This can be changed by using the :ref:`order-scope` option.

Ordering is done either absolutely, by using ordinal numbers that define the
order, or relative to other tests, using the ``before`` and ``after``
attributes of the marker.

Ordering by numbers
-------------------
The order can be defined by ordinal numbers, or by ordinal strings.

Order by index
~~~~~~~~~~~~~~
As already shown above, the order can be defined using ordinal numbers.
There is a long form that uses the keyword ``index``, and a short form, that
uses just the ordinal number--both are shown in the example below. The long
form may be better readable if you want to combine it with a dependency marker
(``before`` or ``after``, see below).
Negative numbers are also allowed--they are used the same way as indices
are used in Python lists, e.g. to count from the end:

.. code:: python

 import pytest

 @pytest.mark.order(-2)
 def test_three():
     assert True

 @pytest.mark.order(index=-1)
 def test_four():
     assert True

 @pytest.mark.order(index=2)
 def test_two():
     assert True

 @pytest.mark.order(1)
 def test_one():
     assert True

::

    $ pytest test_foo.py -vv
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
~~~~~~~~~~~~~~~~~~~~

Instead of the numbers, you can use ordinal names such as "first", "second",
"last", and "second_to_last". These are convenience notations, and have the
same effect as the numbers 0, 1, -1 and -2, respectively, that have been shown
above:

.. code:: python

 import pytest

 @pytest.mark.order("second_to_last")
 def test_three():
     assert True

 @pytest.mark.order("last")
 def test_four():
     assert True

 @pytest.mark.order("second")
 def test_two():
     assert True

 @pytest.mark.order("first")
 def test_one():
     assert True

::

    $ pytest test_foo.py -vv
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

- "first": 0
- "second": 1
- "third": 2
- "fourth": 3
- "fifth": 4
- "sixth": 5
- "seventh": 6
- "eighth": 7
- "last": -1
- "second_to_last": -2
- "third_to_last": -3
- "fourth_to_last": -4
- "fifth_to_last": -5
- "sixth_to_last": -6
- "seventh_to_last": -7
- "eighth_to_last": -8

Handling of unordered tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~
By default, tests with no ``order`` mark are executed after all tests with
positive ordinal numbers (or the respective names), and before tests with
negative ordinal numbers. The order of these tests in relationship to each
other is not changed. This behavior will slightly change if the option
:ref:`sparse-ordering` is used and the ordinals are not contiguous.


Order relative to other tests
-----------------------------

The test order can be defined relative to other tests, which are referenced
by their name:

.. code:: python

 import pytest

 @pytest.mark.order(after="test_second")
 def test_third():
     assert True

 def test_second():
     assert True

 @pytest.mark.order(before="test_second")
 def test_first():
     assert True

::

    $ pytest test_foo.py -vv
    ============================= test session starts ==============================
    platform darwin -- Python 3.7.1, pytest-5.4.3, py-1.8.1, pluggy-0.13.1 -- env/bin/python
    plugins: order
    collected 3 items

    test_foo.py:11: test_first PASSED
    test_foo.py:7: test_second PASSED
    test_foo.py:4: test_third PASSED

    =========================== 4 passed in 0.02 seconds ===========================

Referencing of tests in other classes or modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If a test is referenced using the unqualified test name as shown in the
example above, the test is assumed to be in the current module and the current
class, if any. For tests in other classes in the same module the class name
with a ``::`` suffix has to be prepended to the test name:

.. code:: python

 import pytest

 class TestA:
     @pytest.mark.order(after="TestB::test_c")
     def test_a(self):
         assert True

     def test_b(self):
         assert True

 class TestB:
     def test_c(self):
         assert True

If the referenced test lives in another module, the test name has to be
prepended by the module path to be uniquely identifiable. Let's say we have
the following module and test layout:

::

  test_module_a.py
      TestA
          test_a
          test_b
  test_module_b.py
      test_a
      test_b
  test_module_c
      test_submodule.py
          test_1
          test_2

Suppose the tests in ``test_module_b`` shall depend on tests in the other
modules, this could be expressed like:

**test_module_b.py**

.. code:: python

 import pytest

 @pytest.mark.order(after="test_module_a.TestA::test_a")
 def test_a():
     assert True

 @pytest.mark.order(before="test_module_c.test_submodule.test_2")
 def test_b():
     assert True

If an unknown test is referenced, a warning is issued and the test in
question is ordered behind all other tests.

Combination of absolute and relative ordering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you combine absolute and relative order markers, the ordering is first done
for the absolute markers (e.g. the ordinals), and afterwards for the relative
ones. This means that relative ordering always takes preference:

.. code:: python

 import pytest

 @pytest.mark.order(index=0, after="test_second")
 def test_first():
     assert True

 @pytest.mark.order(1)
 def test_second():
     assert True

In this case, ``test_second`` will be executed before ``test_first``,
regardless of the ordinal markers.

Relationship with pytest-dependency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The `pytest-dependency <https://pypi.org/project/pytest-dependency/>`__
plugin also manages dependencies between tests (skips tests that depend
on skipped or failed tests), but currently doesn't do any ordering. If you
want to execute the tests in a specific order to each other, you can use
``pytest-order``. If you want to skip or xfail tests dependent on other
tests you can use ``pytest-dependency``. If you want to have both behaviors
combined, you can use both plugins together with the
option :ref:`order-dependencies`, described below.

Configuration
=============
There are a few command line options that change the behavior of the
plugin. As with any pytest option, you can add the options to your
``pytest.ini`` if you want to have them applied to all tests automatically:

.. code::

  [pytest]
  ; always order tests with dependency markers
  addopts = --order-dependencies

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

For example consider two test modules:

**tests/test_module1.py**:

.. code::

  import pytest

  @pytest.mark.order(2)
  def test2():
      pass

  @pytest.mark.order(1)
  def test1():
      pass

**tests/test_module2.py**:

.. code::

  import pytest

  @pytest.mark.order(2)
  def test2():
      pass

  @pytest.mark.order(1)
  def test1():
      pass

Here is what you get using session and module-scoped sorting:

::

    $ pytest tests -vv
    ============================= test session starts ==============================
    ...

    tests/test_module1.py:9: test1 PASSED
    tests/test_module2.py:9: test1 PASSED
    tests/test_module1.py:5: test2 PASSED
    tests/test_module2.py:5: test2 PASSED


::

    $ pytest tests -vv --order-scope=module
    ============================= test session starts ==============================
    ...

    tests/test_module1.py:9: test1 PASSED
    tests/test_module1.py:5: test2 PASSED
    tests/test_module2.py:9: test1 PASSED
    tests/test_module2.py:5: test2 PASSED


``--order-group-scope``
-----------------------
This option is also related to the order scope. It defines the scope inside
which tests may be reordered. Consider you have several test modules which
you want to order, but you don't want to mix the tests of several modules
because the module setup is costly. In this case you can set the group order
scope to "module", meaning that first the tests are ordered inside each
module (the same as with the module order scope), but afterwards the modules
themselves are sorted without changing the order inside each module.

Consider these two test modules:

**tests/test_module1.py**:

.. code::

  import pytest

  @pytest.mark.order(2)
  def test1():
      pass

  def test2():
      pass

**tests/test_module2.py**:

.. code::

  import pytest

  @pytest.mark.order(1)
  def test1():
      pass

  def test2():
      pass

Here is what you get using different scopes:

::

    $ pytest tests -vv
    ============================= test session starts ==============================
    ...

    tests/test_module2.py:9: test1 PASSED
    tests/test_module1.py:9: test1 PASSED
    tests/test_module1.py:5: test2 PASSED
    tests/test_module2.py:5: test2 PASSED


::

    $ pytest tests -vv --order-scope=module
    ============================= test session starts ==============================
    ...

    tests/test_module1.py:9: test1 PASSED
    tests/test_module1.py:5: test2 PASSED
    tests/test_module2.py:9: test1 PASSED
    tests/test_module2.py:5: test2 PASSED


::

    $ pytest tests -vv --order-group-scope=module
    ============================= test session starts ==============================
    ...

    tests/test_module2.py:9: test1 PASSED
    tests/test_module2.py:5: test2 PASSED
    tests/test_module1.py:9: test1 PASSED
    tests/test_module1.py:5: test2 PASSED

The ordering of the module groups is done based on the lowest
non-negative order number present in the module (e.g. the order number of
the first test). If only negative numbers are present, the highest negative
number (e.g. the number of the last test) is used, and these modules will be
ordered at the end. Modules without order numbers will be sorted between
modules with a non-negative order number and modules with a negative order
number, the same way tests are sorted inside a module.

The group order scope defaults to the order scope. In this case the tests are
ordered the same way as without the group order scope. The setting takes effect
only if the scope is less than the order scope, e.g. there are three
possibilities:

- order scope "session", order group scope "module" - this is shown in the
  example above: first tests in each module are ordered, afterwards the modules
- order scope "module", order group scope "class" - first orders tests inside
  each class, then the classes inside each module
- order scope "session", order group scope "class" - first orders tests inside
  each class, then the classes inside each module, and finally the modules
  relatively to each other

This option will also work with relative markers.

Here is a similar example using relative markers:

**tests/test_module1.py**:

.. code::

  import pytest

  @pytest.mark.order(after="test_module2.test1")
  def test1():
      pass

  def test2():
      pass

**tests/test_module2.py**:

.. code::

  import pytest

  def test1():
      pass

  @pytest.mark.order(before="test1")
  def test2():
      pass

Here is what you get using different scopes:

::

    $ pytest tests -vv
    ============================= test session starts ==============================
    ...

    tests/test_module1.py:5: test2 PASSED
    tests/test_module2.py:9: test1 PASSED
    tests/test_module2.py:5: test2 PASSED
    tests/test_module1.py:9: test1 PASSED

::

    $ pytest tests -vv --order-group-scope=module
    ============================= test session starts ==============================
    ...

    tests/test_module2.py:9: test1 PASSED
    tests/test_module2.py:5: test2 PASSED
    tests/test_module1.py:9: test1 PASSED
    tests/test_module1.py:5: test2 PASSED

You can see that in the second run the second test module is run before the
first because of the dependency, but the tests inside each module remain in
the same order as before. Note that using module scope as in the example
above doesn't make sense here due to the dependencies between modules.

This will also work with dependency markers if using the
:ref:`order-dependencies` option.


.. note::
  This option will not work together well with the sparse ordering option.

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

.. _sparse-ordering:

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

e.g. you get:

::

    $ pytest tests -vv
    ============================= test session starts ==============================
    ...
    test_module.py:13: test_one PASSED
    test_module.py:3: test_two PASSED
    test_module.py:6: test_three PASSED
    test_module.py:9: test_four PASSED

The gaps between numbers, and the fact that the starting number is not 0,
are ignored. This is consistent with the current behavior of
``pytest-ordering``.

If you use the ``--sparse-ordering`` option, the behavior will change:

::

    $ pytest tests -vv --sparse-ordering
    ============================= test session starts ==============================
    ...
    test_module.py:6: test_three PASSED
    test_module.py:13: test_one PASSED
    test_module.py:9: test_four PASSED
    test_module.py:3: test_two PASSED

Now all missing numbers (starting with 0) are filled with unordered tests, as
long as unordered tests are left. In the shown example, ``test_three``
is filled in for the missing number 0, and ``test_four`` is filled in for the
missing number 2. This will also work for tests with negative order numbers
(or the respective names). The missing ordinals are filled with unordered
tests first from the start, then from the end if there are negative numbers,
and the rest will be in between (e.g. between positive and negative numbers),
as it is without this option.

.. _order-dependencies:

``--order-dependencies``
------------------------
This defines the behavior if the ``pytest-dependency`` plugin is used.
By default, ``dependency`` marks are only considered if they coexist with an
``order`` mark. In this case it is checked if the ordering would break the
dependency, and is ignored if this is the case. Consider the following:

.. code:: python

 import pytest

 def test_a():
     assert True

 @pytest.mark.dependency(depends=["test_a"])
 @pytest.mark.order("first")
 def test_b():
     assert True

In this case, the ordering would break the dependency and is therefore
ignored. This behavior is independent of the option. Now consider the
following tests:

.. code:: python

  import pytest

  @pytest.mark.dependency(depends=["test_b"])
  def test_a():
      assert True

  @pytest.mark.dependency
  def test_b():
      assert True

By default, ``test_a`` is not run, because it depends on ``test_b``, which
is only run after ``test_b``:

::

    $ pytest tests -vv
    ============================= test session starts ==============================
    ...
    test_dep.py::test_a SKIPPED
    test_dep.py::test_b PASSED

If you use ``--order-dependencies``, this will change--the tests will now be
reordered according to the dependency and both run:

::

    $ pytest tests -vv --order-dependencies
    ============================= test session starts ==============================
    ...
    test_dep.py::test_b PASSED
    test_dep.py::test_a PASSED

Note that a similar feature may be added to ``pytest-dependency`` -
if this is done, this option will not be needed, but for the time being you
can use both plugins together to get this behavior.
Note that ``pytest-order`` does not replace ``pytest-dependency``--it just
adds ordering to the existing functionality if needed.

.. note::
  This feature is considered experimental. It may not handle all cases of
  defined dependencies. Please write an issue if you find any problems.


.. note::

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
