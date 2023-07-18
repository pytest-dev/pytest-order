Using pytest-order with other pytest plugins
============================================

Relationship with pytest-dependency
-----------------------------------
The `pytest-dependency`_
plugin also manages dependencies between tests (skips tests that depend
on skipped or failed tests), but doesn't do any ordering. If you
want to execute the tests in a specific order to each other, you can use
``pytest-order``. If you want to skip or xfail tests dependent on other
tests you can use ``pytest-dependency``. If you want to have both behaviors
combined, you can use both plugins together with the
option :ref:`order-dependencies`. As mentioned before, only
static ``dependency`` markers are considered for ordering.

Usage with other ordering plugins
---------------------------------
There is a number of other pytest plugins that change the order in which tests
are executed. Most of these plugins only reorder tests if given some command
line options or in the presence of specific markers (as does ``pytest-order``).
These plugins will not have any effect on ``pytest-order`` if not actively
used. A few plugins always do reordering, most notably ``pytest-randomly``.

`pytest-randomly`_
~~~~~~~~~~~~~~~~~~
This plugin executes tests in a random order to avoid unknown test
dependencies. The plugin is effective if installed and not actively disabled.
``pytest-order`` should still work correctly, because it is executed after
``pytest-randomly`` (except if you use the option
:ref:`indulgent-ordering`). The marked tests will be ordered correctly, but
the order of the unordered tests will change unpredictably. For example, if
you run the following tests:

.. code:: python

 import pytest


 @pytest.mark.order(1)
 def test_second():
     assert True


 def test_third():
     assert True


 def test_fourth():
     assert True


 @pytest.mark.order(0)
 def test_first():
     assert True

the output could either be::

    test_randomly.py::test_first PASSED
    test_randomly.py::test_second PASSED
    test_randomly.py::test_third PASSED
    test_randomly.py::test_fourth PASSED

or:

::

    test_randomly.py::test_first PASSED
    test_randomly.py::test_second PASSED
    test_randomly.py::test_fourth PASSED
    test_randomly.py::test_third PASSED

The same is true for relative ordering. The tests will be correctly ordered
before and after the tests as configured, but all other tests will be in an
arbitrary order. If you want the tests to execute in a random order except the
ones that you know depend on each other, this can be a good strategy to
prevent test dependencies.

If you don't want the installed ``pytest-randomly`` be effective in a test
run, you can exclude it explicitly on the command line::

  python -m pytest -p no:randomly

`pytest-reverse`_
~~~~~~~~~~~~~~~~~
`pytest-reverse`_ is another plugin by the same author to find test
dependencies by running tests in the reverse order. Other than
``pytest-randomly``, it is only effective if the tests are called with the
command line option ``--reverse``.
As with ``pytest-randomly``, you can use this plugin combined with
``pytest-ordering`` to make sure that all known test dependencies are
handled, and possible unknown dependencies are found.

`pytest-random-order`_
~~~~~~~~~~~~~~~~~~~~~~
`pytest-random-order`_ is very similar to ``pytest-randomly``, except that the
tests are only reordered if the option ``--random-order`` is given. Except
from that, what was mentioned for ``pytest-randomly`` is also true for
this plugin.

`pytest-ordering`_
~~~~~~~~~~~~~~~~~~
As mentioned, `pytest-ordering`_ can coexist with ``pytest-order`` due to
the different marker names, but using markers of both plugins in the same test
run is not recommended. One plugin may partially revert the effects of the
other plugin in unpredictable ways, because the order in which they are
executed is not deterministic. The same is true for other plugins that define
the test order and are run last.

`pytest-depends`_
~~~~~~~~~~~~~~~~~
`pytest-depends`_ has a goal somewhat similar to `pytest-dependency`_ with
additional ordering, but due to a known issue it always reorders the tests.
If you have installed this plugin, the order of the unordered tests will
change even without using it actively.

`pytest-find-dependencies`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is a small plugin by the same author as ``pytest-order`` that tries to
find specific dependencies between tests by running a subset of them repeatedly
in reverse order until the dependencies are found. This plugin would run the
tests as ordered by any ordering plugin in the first run, but reverse the
test order in the second run, so that already ordered tests are not run in
the correct order. You have the possibility to exclude ordered tests
completely by using the ``--markers-to-ignore`` option::

  python -m pytest --find-dependencies --markers-to-ignore=order

Usage with pytest-xdist
-----------------------
The `pytest-xdist`_ plugin
schedules tests unordered, and the order configured by ``pytest-order``
will normally not be preserved. But if we use the ``--dist=loadfile``
option, provided by ``xdist``, all tests from one file will be run in the
same thread. So, to make the two plugins work together, we have to put
each group of dependent tests in one file, and call pytest with
``--dist=loadfile`` (this is taken from
`this issue <https://github.com/ftobia/pytest-ordering/issues/36>`__).


.. _`pytest-xdist`: https://pypi.org/project/pytest-xdist/
.. _`pytest-randomly`: https://pypi.org/project/pytest-randomly/
.. _`pytest-dependency`: https://pypi.org/project/pytest-dependency/
.. _`pytest-reverse`: https://pypi.org/project/pytest-reverse/
.. _`pytest-depends`: https://pypi.org/project/pytest-depends/
.. _`pytest-random-order`: https://pypi.org/project/pytest-random-order/
.. _`pytest-find-dependencies`: https://pypi.org/project/pytest-find-dependencies/
.. _`pytest-ordering`: https://pypi.org/project/pytest-ordering/
