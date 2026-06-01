"""
Tests for relative ordering constraints that interact with absolute ordinal markers.

When a test carries both a relative constraint (after=/before=) and the anchor
is pinned to an absolute ordinal position (last, second_to_last, first, …),
the constraint is structurally impossible: relatively-ordered tests always fill
the middle section, between start-ordinal and end-ordinal items.

pytest-order emits a WARNING for each such impossible constraint and preserves
the absolute ordinal positions unchanged.
"""


# ---------------------------------------------------------------------------
# Scenario 1 – simplest transitive chain across three tests
#
#   collection order: test_a, test_b, test_c
#   markers:          test_b must come after test_c
#   desired order:    test_a, test_c, test_b
#
# This already works with the greedy algorithm; it is a baseline sanity check.
# ---------------------------------------------------------------------------
def test_simple_after_chain(item_names_for):
    test_content = """
        import pytest

        def test_a():
            pass

        @pytest.mark.order(after="test_c")
        def test_b():
            pass

        def test_c():
            pass
        """
    assert item_names_for(test_content) == ["test_a", "test_c", "test_b"]


# ---------------------------------------------------------------------------
# Scenario 2 – `after` a second_to_last anchor + `before` a last anchor
#
#   collection order: test_setup, test_middle, test_anchor (second_to_last),
#                     test_last (last)
#   markers:
#     test_anchor  → order("second_to_last")   ← end-ordinal, pinned
#     test_last    → order("last")              ← end-ordinal, pinned
#     test_middle  → after=test_anchor, before=test_last
#
#   `after=test_anchor` is impossible: test_middle is relatively-ordered and
#   always runs before the end-ordinal section.  pytest-order warns and keeps
#   absolute positions intact.
#   actual order: test_setup, test_middle, test_anchor, test_last
# ---------------------------------------------------------------------------
def test_between_absolute_anchors(item_names_for, capsys):
    test_content = """
        import pytest

        def test_setup():
            pass

        @pytest.mark.order(after="test_anchor", before="test_last")
        def test_middle():
            pass

        @pytest.mark.order("second_to_last")
        def test_anchor():
            pass

        @pytest.mark.order("last")
        def test_last():
            pass
        """
    assert item_names_for(test_content) == [
        "test_setup",
        "test_middle",
        "test_anchor",
        "test_last",
    ]
    out, _ = capsys.readouterr()
    assert "cannot place 'test_middle' after 'test_anchor'" in out


# ---------------------------------------------------------------------------
# Scenario 3 – `after` a second_to_last anchor in a relative chain
#
#   collection order: test_a, test_b, test_c, test_d,
#                     test_penultimate (second_to_last), test_final (last)
#   markers:
#     test_penultimate → order("second_to_last")   ← end-ordinal, pinned
#     test_final       → order("last")             ← end-ordinal, pinned
#     test_d           → before=test_final
#     test_c           → before=test_d
#     test_b           → after=test_penultimate, before=test_c
#
#   `after=test_penultimate` is impossible for the same reason as scenario 2.
#   The relative chain test_b→test_c→test_d is resolved correctly.
#   actual order: test_a, test_b, test_c, test_d, test_penultimate, test_final
# ---------------------------------------------------------------------------
def test_after_absolute_before_relative_chain(item_names_for, capsys):
    test_content = """
        import pytest

        def test_a():
            pass

        @pytest.mark.order(after="test_penultimate", before="test_c")
        def test_b():
            pass

        @pytest.mark.order(before="test_d")
        def test_c():
            pass

        @pytest.mark.order(before="test_final")
        def test_d():
            pass

        @pytest.mark.order("second_to_last")
        def test_penultimate():
            pass

        @pytest.mark.order("last")
        def test_final():
            pass
        """
    assert item_names_for(test_content) == [
        "test_a",
        "test_b",
        "test_c",
        "test_d",
        "test_penultimate",
        "test_final",
    ]
    out, _ = capsys.readouterr()
    assert "cannot place 'test_b' after 'test_penultimate'" in out


# ---------------------------------------------------------------------------
# Scenario 4 – cross-module variant of scenario 3
#
#   test_mod_base.py:  test_anchor (second_to_last), test_last (last)
#   test_mod_extra.py: test_x (after=test_mod_base::test_anchor, before=test_y),
#                      test_y (before=test_z),
#                      test_z (before=test_mod_base::test_last)
#
#   `after=test_anchor` is impossible (end-ordinal anchor).  The relative
#   chain test_x→test_y→test_z is satisfied; test_anchor and test_last keep
#   their absolute end positions.
#   actual order: test_x, test_y, test_z, test_anchor, test_last
# ---------------------------------------------------------------------------
def test_after_absolute_before_relative_chain_cross_module(test_path):
    test_path.makepyfile(
        test_mod_base="""
        import pytest

        @pytest.mark.order("second_to_last")
        def test_anchor():
            pass

        @pytest.mark.order("last")
        def test_last():
            pass
        """,
        test_mod_extra="""
        import pytest

        @pytest.mark.order(after="test_mod_base.py::test_anchor", before="test_y")
        def test_x():
            pass

        @pytest.mark.order(before="test_z")
        def test_y():
            pass

        @pytest.mark.order(before="test_mod_base.py::test_last")
        def test_z():
            pass
        """,
    )
    result = test_path.runpytest("-v")
    result.assert_outcomes(passed=5)
    result.stdout.fnmatch_lines(
        [
            "test_mod_extra.py::test_x PASSED",
            "test_mod_extra.py::test_y PASSED",
            "test_mod_extra.py::test_z PASSED",
            "test_mod_base.py::test_anchor PASSED",
            "test_mod_base.py::test_last PASSED",
        ]
    )
    assert "cannot place 'test_x' after 'test_anchor'" in result.stdout.str()


# ---------------------------------------------------------------------------
# Scenario 5 – longer transitive chain, all relative (no absolute ordering)
#
#   collection order: test_1, test_2, test_3, test_4, test_5
#   markers:          test_3 after test_5  →  desired: …, test_5, test_3
#                     test_2 after test_3  →  desired: …, test_5, test_3, test_2
#                     test_4 after test_2  →  desired: test_1, test_5, test_3,
#                                                       test_2, test_4
# ---------------------------------------------------------------------------
def test_long_transitive_chain(item_names_for):
    test_content = """
        import pytest

        def test_1():
            pass

        @pytest.mark.order(after="test_3")
        def test_2():
            pass

        @pytest.mark.order(after="test_5")
        def test_3():
            pass

        @pytest.mark.order(after="test_2")
        def test_4():
            pass

        def test_5():
            pass
        """
    assert item_names_for(test_content) == [
        "test_1",
        "test_5",
        "test_3",
        "test_2",
        "test_4",
    ]


# ---------------------------------------------------------------------------
# Scenario 6 – regression guard: existing simple cases must still work
#              (ensures the fix doesn't regress the happy paths)
# ---------------------------------------------------------------------------
def test_simple_before_still_works(item_names_for):
    test_content = """
        import pytest

        def test_a():
            pass

        @pytest.mark.order(before="test_a")
        def test_b():
            pass
        """
    assert item_names_for(test_content) == ["test_b", "test_a"]


def test_simple_after_still_works(item_names_for):
    test_content = """
        import pytest

        @pytest.mark.order(after="test_b")
        def test_a():
            pass

        def test_b():
            pass
        """
    assert item_names_for(test_content) == ["test_b", "test_a"]


def test_absolute_last_still_works(item_names_for):
    test_content = """
        import pytest

        @pytest.mark.order("last")
        def test_a():
            pass

        def test_b():
            pass

        def test_c():
            pass
        """
    assert item_names_for(test_content) == ["test_b", "test_c", "test_a"]
