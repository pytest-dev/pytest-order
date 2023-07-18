import pytest


@pytest.fixture
def fixture_path(test_path):
    test_path.makepyfile(
        test_rel1=(
            """
            import pytest

            class Test1:
                @pytest.mark.order(after='Test2::test_two')
                def test_one(self):
                    assert True

                def test_two(self):
                    assert True

            class Test2:
                @pytest.mark.order(after='invalid')
                def test_one(self):
                    assert True

                @pytest.mark.order(after='test_rel3.py::test_two')
                def test_two(self):
                    assert True
            """
        ),
        test_rel2=(
            """
            def test_one():
                assert True

            def test_two():
                assert True
            """
        ),
        test_rel3=(
            """
            import pytest

            def test_one():
                assert True

            @pytest.mark.order(before='test_rel2.py::test_one')
            def test_two():
                assert True
            """
        ),
        test_rel4=(
            """
            import pytest

            def test_one():
                assert True

            def test_two():
                assert True
            """
        ),
    )
    yield test_path


def test_session_scope(fixture_path):
    result = fixture_path.runpytest("-v")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "*'invalid' - ignoring the marker.*",
            "test_rel1.py::Test1::test_two PASSED",
            "test_rel1.py::Test2::test_one PASSED",
            "test_rel3.py::test_two PASSED",
            "test_rel1.py::Test2::test_two PASSED",
            "test_rel1.py::Test1::test_one PASSED",
            "test_rel2.py::test_one PASSED",
            "test_rel2.py::test_two PASSED",
            "test_rel3.py::test_one PASSED",
            "test_rel4.py::test_one PASSED",
            "test_rel4.py::test_two PASSED",
        ]
    )


def test_module_group_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-group-scope=module")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_rel3.py::test_one PASSED",
            "test_rel3.py::test_two PASSED",
            "test_rel1.py::Test1::test_two PASSED",
            "test_rel1.py::Test2::test_one PASSED",
            "test_rel1.py::Test2::test_two PASSED",
            "test_rel1.py::Test1::test_one PASSED",
            "test_rel2.py::test_one PASSED",
            "test_rel2.py::test_two PASSED",
            "test_rel4.py::test_one PASSED",
            "test_rel4.py::test_two PASSED",
        ]
    )


def test_class_group_scope(fixture_path):
    result = fixture_path.runpytest("-v", "--order-group-scope=class")
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_rel3.py::test_one PASSED",
            "test_rel3.py::test_two PASSED",
            "test_rel1.py::Test2::test_one PASSED",
            "test_rel1.py::Test2::test_two PASSED",
            "test_rel1.py::Test1::test_one PASSED",
            "test_rel1.py::Test1::test_two PASSED",
            "test_rel2.py::test_one PASSED",
            "test_rel2.py::test_two PASSED",
            "test_rel4.py::test_one PASSED",
            "test_rel4.py::test_two PASSED",
        ]
    )


def test_class_group_scope_module_scope(fixture_path):
    result = fixture_path.runpytest(
        "-v", "--order-group-scope=class", "--order-scope=module"
    )
    result.assert_outcomes(passed=10, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_rel1.py::Test2::test_one PASSED",
            "test_rel1.py::Test2::test_two PASSED",
            "test_rel1.py::Test1::test_one PASSED",
            "test_rel1.py::Test1::test_two PASSED",
            "test_rel2.py::test_one PASSED",
            "test_rel2.py::test_two PASSED",
            "test_rel3.py::test_one PASSED",
            "test_rel3.py::test_two PASSED",
            "test_rel4.py::test_one PASSED",
            "test_rel4.py::test_two PASSED",
        ]
    )


def test_rel_class_mark_with_order_mark(test_path):
    test_path.makepyfile(
        test_class_rel="""
        import pytest

        class Test1:
            def test_1(self): pass

            @pytest.mark.order(1)
            def test_2(self): pass

        @pytest.mark.order(before="Test1")
        class Test2:
            def test_1(self): pass

            @pytest.mark.order(1)
            def test_2(self): pass
        """
    )
    result = test_path.runpytest("-v", "--order-group-scope=class")
    result.assert_outcomes(passed=4, failed=0)
    result.stdout.fnmatch_lines(
        [
            "test_class_rel.py::Test2::test_2 PASSED",
            "test_class_rel.py::Test2::test_1 PASSED",
            "test_class_rel.py::Test1::test_2 PASSED",
            "test_class_rel.py::Test1::test_1 PASSED",
        ]
    )
