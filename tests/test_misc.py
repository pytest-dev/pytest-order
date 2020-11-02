# -*- coding: utf-8 -*-
import re

import pytest

import pytest_order


def test_version_exists():
    assert hasattr(pytest_order, "__version__")


def test_version_valid():
    assert re.match(r"[0-9]+\.[0-9]+(\.[0-9]+)?(dev)?$",
                    pytest_order.__version__)


def test_markers_registered(capsys):
    pytest.main(["--markers"])
    out, err = capsys.readouterr()
    assert "@pytest.mark.order" in out
    # only order is supported as marker
    assert out.count("Provided by pytest-order.") == 1
