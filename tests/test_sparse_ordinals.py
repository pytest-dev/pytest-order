import pytest


@pytest.fixture
def sparse_ordering(ignore_settings):
    ignore_settings.return_value.sparse_ordering = True
    yield


@pytest.fixture(scope="module")
def first_test():
    yield (
        """
        import pytest

        def test_1(): pass

        @pytest.mark.order("first")
        def test_2(): pass
        """
    )


def test_first_default(first_test, item_names_for):
    assert item_names_for(first_test) == ["test_2", "test_1"]


def test_first_sparse(first_test, item_names_for, sparse_ordering):
    assert item_names_for(first_test) == ["test_2", "test_1"]


@pytest.fixture(scope="module")
def second_test():
    yield (
        """
        import pytest

        def test_1(): pass
        def test_2(): pass
        def test_3(): pass
        def test_4(): pass

        @pytest.mark.order("second")
        def test_5(): pass
        """
    )


def test_second_default(second_test, item_names_for):
    assert item_names_for(second_test) == [
        "test_5",
        "test_1",
        "test_2",
        "test_3",
        "test_4",
    ]


def test_second_sparse(second_test, item_names_for, sparse_ordering):
    assert item_names_for(second_test) == [
        "test_1",
        "test_5",
        "test_2",
        "test_3",
        "test_4",
    ]


@pytest.fixture(scope="module")
def third_test():
    yield (
        """
        import pytest

        def test_1(): pass
        def test_2(): pass
        def test_3(): pass

        @pytest.mark.order("third")
        def test_4(): pass

        def test_5(): pass
        """
    )


def test_third_default(third_test, item_names_for):
    assert item_names_for(third_test) == [
        "test_4",
        "test_1",
        "test_2",
        "test_3",
        "test_5",
    ]


def test_third_sparse(third_test, item_names_for, sparse_ordering):
    assert item_names_for(third_test) == [
        "test_1",
        "test_2",
        "test_4",
        "test_3",
        "test_5",
    ]


@pytest.fixture(scope="module")
def second_to_last_test():
    yield (
        """
        import pytest

        def test_1(): pass

        @pytest.mark.order("second_to_last")
        def test_2(): pass

        def test_3(): pass
        def test_4(): pass
        def test_5(): pass
        """
    )


def test_second_to_last_default(second_to_last_test, item_names_for):
    assert item_names_for(second_to_last_test) == [
        "test_1",
        "test_3",
        "test_4",
        "test_5",
        "test_2",
    ]


def test_second_to_last_sparse(second_to_last_test, item_names_for, sparse_ordering):
    assert item_names_for(second_to_last_test) == [
        "test_1",
        "test_3",
        "test_4",
        "test_2",
        "test_5",
    ]


@pytest.fixture(scope="module")
def last_test():
    yield (
        """
        import pytest

        @pytest.mark.order("last")
        def test_1(): pass

        def test_2(): pass
        """
    )


def test_last_default(last_test, item_names_for):
    assert item_names_for(last_test) == ["test_2", "test_1"]


def test_last_sparse(last_test, item_names_for, sparse_ordering):
    assert item_names_for(last_test) == ["test_2", "test_1"]


@pytest.fixture(scope="module")
def first_last_test():
    yield (
        """
        import pytest

        @pytest.mark.order("last")
        def test_1(): pass

        @pytest.mark.order("first")
        def test_2(): pass

        def test_3(): pass
        """
    )


def test_first_last_default(first_last_test, item_names_for):
    assert item_names_for(first_last_test) == ["test_2", "test_3", "test_1"]


def test_first_last_sparse(first_last_test, item_names_for, sparse_ordering):
    assert item_names_for(first_last_test) == ["test_2", "test_3", "test_1"]


@pytest.fixture(scope="module")
def duplicate_numbers_test():
    yield (
        """
        import pytest

        @pytest.mark.order(1)
        def test_1(): pass

        @pytest.mark.order(1)
        def test_2(): pass

        def test_3(): pass

        def test_4(): pass

        @pytest.mark.order(4)
        def test_5(): pass
        """
    )


def test_duplicate_numbers_default(duplicate_numbers_test, item_names_for):
    assert item_names_for(duplicate_numbers_test) == [
        "test_1",
        "test_2",
        "test_5",
        "test_3",
        "test_4",
    ]


def test_duplicate_numbers_sparse(
    duplicate_numbers_test, item_names_for, sparse_ordering
):
    assert item_names_for(duplicate_numbers_test) == [
        "test_3",
        "test_1",
        "test_2",
        "test_4",
        "test_5",
    ]


@pytest.fixture(scope="module")
def end_items_test():
    yield (
        """
        import pytest

        @pytest.mark.order(-2)
        def test_1(): pass

        @pytest.mark.order(-4)
        def test_2(): pass

        def test_3(): pass

        def test_4(): pass

        def test_5(): pass
        """
    )


def test_end_items_default(end_items_test, item_names_for):
    assert item_names_for(end_items_test) == [
        "test_3",
        "test_4",
        "test_5",
        "test_2",
        "test_1",
    ]


def test_end_items_sparse(end_items_test, item_names_for, sparse_ordering):
    assert item_names_for(end_items_test) == [
        "test_3",
        "test_2",
        "test_4",
        "test_1",
        "test_5",
    ]
