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

Markers on class level
~~~~~~~~~~~~~~~~~~~~~~
If setting an ``order`` mark on class level, all tests in this class will be
handled as having the same ordinal marker, e.g. the class as a whole will be
reordered without changing the test order inside the test class:

.. code:: python

    import pytest


    @pytest.mark.order(1)
    class Test1:
        def test_1(self):
            assert True

        def test_2(self):
            assert True


    @pytest.mark.order(0)
    class Test2:
        def test_1(self):
            assert True

        def test_2(self):
            assert True

::

    $ pytest -vv test_ordinal_class_mark.py
    ============================= test session starts ==============================
    ...
    collected 4 items

    test_ordinal_class_mark.py::Test2::test_1 PASSED
    test_ordinal_class_mark.py::Test2::test_2 PASSED
    test_ordinal_class_mark.py::Test1::test_1 PASSED
    test_ordinal_class_mark.py::Test1::test_2 PASSED


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
by their name. The marker attributes ``before`` and ``after`` can be used to
define the order relative to these tests:

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

If the referenced test lives in another module, you have to use the nodeid
of the test, or a part of the nodeid that is sufficient to make it uniquely
identifiable (the nodeid is the test ID that pytest prints if you run it with
the ``-v`` option).
Let's say we have the following module and test layout::

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


 @pytest.mark.order(after="test_module_a.py::TestA::test_a")
 def test_a():
     assert True


 @pytest.mark.order(before="test_module_c/test_submodule.py::test_2")
 def test_b():
     assert True

If an unknown test is referenced, a warning is issued and the execution
order of the test in is not changed.

Markers on class level
~~~~~~~~~~~~~~~~~~~~~~
As for ordinal markers, markers on class level are handled as if they are set
to each individual test in the class. Additionally to referencing single
tests, you can also reference test classes if using the ``before`` or
``after`` marker attributes:

.. code:: python

    import pytest


    @pytest.mark.order(after="Test2")
    class Test1:
        def test_1(self):
            assert True

        def test_2(self):
            assert True


    class Test2:
        def test_1(self):
            assert True

        def test_2(self):
            assert True

In this case, the tests in the marked class will be ordered behind all tests
in the referenced class::

    $ pytest -vv test_relative_class_mark.py
    ============================= test session starts ==============================
    ...
    collected 4 items

    test_relative_class_marker.py::Test2::test_1 PASSED
    test_relative_class_marker.py::Test2::test_2 PASSED
    test_relative_class_marker.py::Test1::test_1 PASSED
    test_relative_class_marker.py::Test1::test_2 PASSED

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

Several relationships for the same marker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you need to order a certain test relative to more than one other test, you
can add more than one test name to the ``before`` or ``after`` marker
attributes by using a list or tuple of test names:

.. code:: python

 import pytest


 @pytest.mark.order(after=["test_second", "other_module.py::test_other"])
 def test_first():
     assert True


 def test_second():
     assert True

This will ensure that ``test_first`` is executed both after ``test_second``
and after ``test_other`` which resides in the module ``other_module.py``.

Relationships with parameterized tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to reference parametrized tests, you can just use the test name
without the parameter part, for example:

.. code:: python

 import pytest


 @pytest.mark.order(after=["test_second"])
 def test_first():
     assert True


 @pytest.parametrize(param, [1, 2, 3])
 def test_second(param):
     assert True

Note that using the fully qualified test name, which would include the
parameter (in this case ``test_second[1]``, ``test_second[2]`` etc) is not
supported.


Multiple test order markers
---------------------------
More than one order marker can be set for the test.
In this scenario test will be executed several times in the defined order.

Combination of absolute and relative ordering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

 import pytest


 @pytest.mark.order(1)
 @pytest.mark.order(-1)
 def test_one_and_seven():
     pass


 @pytest.mark.order(2)
 @pytest.mark.order(-2)
 def test_two_and_six():
     pass


 def test_four():
     pass


 @pytest.mark.order(before="test_four")
 @pytest.mark.order(after="test_four")
 def test_three_and_five():
     pass

When a test has multiple order markers, each marker turns into a pytest ``ParameterSet``,
so it will be run multiple times.

::

    ============================= test session starts =============================
    collecting ... collected 7 items
    test_multiple_markers.py::test_one_and_seven[index=1]
    test_multiple_markers.py::test_two_and_six[index=2]
    test_multiple_markers.py::test_three_and_five[before=test_four]
    test_multiple_markers.py::test_four
    test_multiple_markers.py::test_three_and_five[after=test_four]
    test_multiple_markers.py::test_two_and_six[index=-2]
    test_multiple_markers.py::test_one_and_seven[index=-1]
    ============================== 7 passed in 0.02s ==============================


Parametrized tests
~~~~~~~~~~~~~~~~~~
Although multiple test order markers create their own parametrization, it can be used with parametrized tests.

.. code:: python

 import pytest


 @pytest.mark.order(1)
 @pytest.mark.order(3)
 @pytest.mark.parametrize("foo", ["aaa", "bbb"])
 def test_one_and_three(foo):
     pass


 @pytest.mark.order(4)
 @pytest.mark.parametrize("bar", ["bbb", "ccc"])
 @pytest.mark.order(2)
 def test_two_and_four(bar):
     pass

::

    collecting ... collected 8 items
    test_multiple_markers.py::test_one_and_three[index=1-aaa] PASSED         [ 12%]
    test_multiple_markers.py::test_one_and_three[index=1-bbb] PASSED         [ 25%]
    test_multiple_markers.py::test_two_and_four[index=2-bbb] PASSED          [ 37%]
    test_multiple_markers.py::test_two_and_four[index=2-ccc] PASSED          [ 50%]
    test_multiple_markers.py::test_one_and_three[index=3-aaa] PASSED         [ 62%]
    test_multiple_markers.py::test_one_and_three[index=3-bbb] PASSED         [ 75%]
    test_multiple_markers.py::test_two_and_four[index=4-bbb] PASSED          [ 87%]
    test_multiple_markers.py::test_two_and_four[index=4-ccc] PASSED          [100%]
    ============================== 8 passed in 0.02s ==============================
