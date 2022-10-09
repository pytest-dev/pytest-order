"""One of the example files showing relative ordering between modules.
See https://pytest-order.readthedocs.io/en/stable/#referencing-of-tests-in-other-classes-or-modules  # noqa: E501
"""


class TestA:
    def test_a(self):
        assert True

    def test_b(self):
        assert True
