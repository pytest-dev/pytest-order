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

Here is what you get using session and module-scoped sorting::

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


``--order-scope-level``
-----------------------
This is an alternative option to define the order scope. It defines the
directory level which is used as the order scope, counting from the root
directory. The resulting scope is between the session and module
scopes defined via ``--order-scope``, where ``--order-scope-level=0`` is the
same as session scope, while setting the level to the number of test
directory levels would result in module scope.

Consider the following directory structure::

  order_scope_level
    feature1
      __init__.py
      test_a.py
      test_b.py
    feature2
      __init__.py
      test_a.py
      test_b.py

with the test contents:

**test_a.py**:

.. code::

  import pytest

  @pytest.mark.order(4)
  def test_four():
      pass

  @pytest.mark.order(3)
  def test_three():
      pass

**test_b.py**:

.. code::

  import pytest

  @pytest.mark.order(2)
  def test_two():
      pass

  @pytest.mark.order(1)
  def test_one():
      pass

The idea here is to test each feature separately, while ordering the tests
across the test modules for each feature.

If we use session scope, we get::

    $ pytest -v order_scope_level
    ============================= test session starts ==============================
    ...

    order_scope_level/feature1/test_a.py::test_one PASSED
    order_scope_level/feature2/test_a.py::test_one PASSED
    order_scope_level/feature1/test_a.py::test_two PASSED
    order_scope_level/feature2/test_a.py::test_two PASSED
    order_scope_level/feature1/test_b.py::test_three PASSED
    order_scope_level/feature2/test_b.py::test_three PASSED
    order_scope_level/feature1/test_b.py::test_four PASSED
    order_scope_level/feature2/test_b.py::test_four PASSED

which mixes the features.

Using module scope instead separates the features, but does not order the
modules as wanted::

    $ pytest -v --order-scope=module order_scope_level
    ============================= test session starts ==============================
    ...

    order_scope_level/feature1/test_a.py::test_three PASSED
    order_scope_level/feature1/test_a.py::test_four PASSED
    order_scope_level/feature1/test_b.py::test_one PASSED
    order_scope_level/feature1/test_b.py::test_two PASSED
    order_scope_level/feature2/test_a.py::test_three PASSED
    order_scope_level/feature2/test_a.py::test_four PASSED
    order_scope_level/feature2/test_b.py::test_one PASSED
    order_scope_level/feature2/test_b.py::test_two PASSED

To get the wanted behavior, we can use ``--order-scope-level=2``, which keeps
the first two directory levels::

    $ pytest tests -v --order-scope-level=2 order_scope_level
    ============================= test session starts ==============================
    ...

    order_scope_level/feature1/test_b.py::test_one PASSED
    order_scope_level/feature1/test_b.py::test_two PASSED
    order_scope_level/feature1/test_a.py::test_three PASSED
    order_scope_level/feature1/test_a.py::test_four PASSED
    order_scope_level/feature2/test_b.py::test_one PASSED
    order_scope_level/feature2/test_b.py::test_two PASSED
    order_scope_level/feature2/test_a.py::test_three PASSED
    order_scope_level/feature2/test_a.py::test_four PASSED

Note that using a level of 0 or 1 would cause the same result as session
scope in this example, and any level greater than 2 would emulate module scope.

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

Here is what you get using different scopes::

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

This option will also work with relative markers, and with dependency markers
if using the :ref:`order-dependencies` option.

Here is a similar example using relative markers:

**tests/test_module1.py**:

.. code::

  import pytest

  @pytest.mark.order(after="test_module2.py::test1")
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

Here is what you get using different scopes::

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

.. _order-dependencies:

``--order-dependencies``
------------------------
This defines the behavior if the `pytest-dependency`_ plugin is used.
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
is only run after ``test_b``::

    $ pytest tests -vv
    ============================= test session starts ==============================
    ...
    test_dep.py::test_a SKIPPED
    test_dep.py::test_b PASSED

If you use ``--order-dependencies``, this will change--the tests will now be
reordered according to the dependency and both run::

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
  ``pytest-dependency`` also has the possibility to `add dependencies at
  runtime`_ using ``pytest_dependency.depends``. These dependencies cannot be
  detected at collection time and therefore are not included in ordering.
  The same is true for the `dynamic compilation of marked parameters`_.

.. _order-marker-prefix:

``--order-marker-prefix``
-------------------------
Consider the following: You have several groups of tests where you want to decide
which test groups to execute in a certain test run. This is usually done using custom markers,
so that you can filter the tests by the markers using the "-m" option:

.. code:: python

  import pytest


  @pytest.mark.m3
  def test_a():
      assert True


  @pytest.mark.m1
  def test_b():
      assert True


  @pytest.mark.m2
  def test_c():
      assert True

Running these you get::

    $ pytest tests -vv -m "m2 or m3"
    ============================= test session starts ==============================
    ...
    test_module.py:5: test_a PASSED
    test_module.py:15: test_c PASSED

Now consider that the test groups shall always be executed in a certain order, e.g.
the group with the marker "m1" shall always be executed before the tests with "m2" etc.
This can be achieved by adding an additional order marker to each test:

.. code:: python

  import pytest


  @pytest.mark.order(3)
  @pytest.mark.m3
  def test_a():
      assert True


  @pytest.mark.order(1)
  @pytest.mark.m1
  def test_b():
      assert True

etc. Running these you get the desired order::

    $ pytest tests -vv -m "m2 or m3"
    ============================= test session starts ==============================
    ...
    test_module.py:18: test_c PASSED
    test_module.py:6: test_a PASSED

This looks redundant and is also error-prone. If you want to order them instead
just using your own marker (which has the order index already in the name), you can use
the option ``--order-marker-prefix``. Running the original tests without any order marker
gives you now::

    $ pytest tests -vv -m "m2 or m3" --order-merker-prefix=m
    ============================= test session starts ==============================
    ...
    test_module.py:18: test_c PASSED
    test_module.py:6: test_a PASSED

.. note::
  As usually, you are responsible for registering your own markers, either in the
  code or in the ``pytest.ini`` file. If you forget this, pytest will give you warnings about unknown markers.

.. _indulgent-ordering:

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

e.g. you get::

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

If you use the ``--sparse-ordering`` option, the behavior will change::

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

.. _`pytest-dependency`: https://pypi.org/project/pytest-dependency/
.. _`dynamic compilation of marked parameters`: https://pytest-dependency.readthedocs.io/en/stable/advanced.html#dynamic-compilation-of-marked-parameters
.. _`add dependencies at runtime`: https://pytest-dependency.readthedocs.io/en/stable/usage.html#marking-dependencies-at-runtime
