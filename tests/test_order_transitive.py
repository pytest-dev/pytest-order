"""
Tests for relative ordering constraints that interact with absolute ordinal markers.

Absolute ordinals (first, last, second_to_last, index=N, …) only provide a
baseline order. Relative constraints (after=/before=) always take preference:
when a relative constraint conflicts with an anchor's ordinal position, the
ordinal is relaxed so the relative constraint is satisfied (see "Combination of
absolute and relative ordering" in the docs).

These tests also cover transitive relative chains, which are resolved as a
single globally-consistent order rather than by greedy pairwise moves.
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
#     test_anchor  → order("second_to_last")
#     test_last    → order("last")
#     test_middle  → after=test_anchor, before=test_last
#
#   Relative ordering takes preference: test_middle is placed after test_anchor
#   and before test_last, relaxing test_anchor's second_to_last position.
#   order: test_setup, test_anchor, test_middle, test_last
# ---------------------------------------------------------------------------
def test_between_absolute_anchors(item_names_for):
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
        "test_anchor",
        "test_middle",
        "test_last",
    ]


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
#   Relative ordering takes preference: test_b is placed after test_penultimate
#   (relaxing its second_to_last position) and the chain test_b→test_c→test_d→
#   test_final is satisfied.
#   order: test_a, test_penultimate, test_b, test_c, test_d, test_final
# ---------------------------------------------------------------------------
def test_after_absolute_before_relative_chain(item_names_for):
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
        "test_penultimate",
        "test_b",
        "test_c",
        "test_d",
        "test_final",
    ]


# ---------------------------------------------------------------------------
# Scenario 4 – cross-module variant of scenario 3
#
#   test_mod_base.py:  test_anchor (second_to_last), test_last (last)
#   test_mod_extra.py: test_x (after=test_mod_base::test_anchor, before=test_y),
#                      test_y (before=test_z),
#                      test_z (before=test_mod_base::test_last)
#
#   Relative ordering takes preference across modules too: test_x is placed
#   after test_anchor (relaxing its second_to_last position) and the chain
#   test_x→test_y→test_z→test_last is satisfied.
#   order: test_anchor, test_x, test_y, test_z, test_last
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
            "test_mod_base.py::test_anchor PASSED",
            "test_mod_extra.py::test_x PASSED",
            "test_mod_extra.py::test_y PASSED",
            "test_mod_extra.py::test_z PASSED",
            "test_mod_base.py::test_last PASSED",
        ]
    )


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
