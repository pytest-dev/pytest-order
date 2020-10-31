# -*- coding: utf-8 -*-
import re

import pytest_order


def test_version_exists():
    assert hasattr(pytest_order, "__version__")


def test_version_valid():
    assert re.match(r"[0-9]+\.[0-9]+(\.[0-9]+)?(dev)?$",
                    pytest_order.__version__)
