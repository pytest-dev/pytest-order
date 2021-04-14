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
option :ref:`order-dependencies`, described above. As mentioned before, only
static ``dependency`` markers are considered for ordering.

Usage with other ordering plugins
---------------------------------
There is a number of other pytest plugins that change the order in which tests
are executed, the most widely known probably being
`pytest-randomly`_, which
executes tests in a random order to avoid unknown test dependencies.
``pytest-order`` should still work with these as long as it is executed
*after* the other plugins (which it should by default, except if you use
the option :ref:`indulgent-ordering`).
The marked tests still shall be ordered correctly, but the order of the
unordered tests will change, depending on the order the tests have been
after these other plugins have reordered them.
For example, if you have installed ``pytest-randomly``, and run the
following tests:

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
arbitrary order.

Note that it does not make much sense to use ordering plugins together that
have a similar goal as ``pytest-order``, as for example ``pytest-ordering``.
As mentioned, both plugins can co-exist without problems due to the
different marker names, but using markers of both plugins in the same test
run is not recommended. One plugin may partially revert the effects of the
other plugin in unpredictable ways. The same is true for other plugins that
define the test order.

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
