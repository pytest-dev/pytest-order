"""One of the example files showing relative ordering between modules.
See https://mrbean-bremen.github.io/pytest-order/dev/#referencing-of-tests-in-other-classes-or-modules  # noqa: E501
"""


class TestA:
    def test_a(self):
        assert True

    def test_b(self):
        assert True
