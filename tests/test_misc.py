# -*- coding: utf-8 -*-
import re

import pytest

import pytest_order


def test_version_exists():
    assert hasattr(pytest_order, "__version__")


def test_version_valid():
    # check for PEP 440 conform version
    assert re.match(r"\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d)?(\.dev\d)?$",
                    pytest_order.__version__)


def test_markers_registered(capsys):
    pytest.main(["--markers"])
    out, err = capsys.readouterr()
    assert "@pytest.mark.order" in out
    # only order is supported as marker
    assert out.count("Provided by pytest-order.") == 1
