# -*- coding: utf-8 -*-
import re

import pytest_ordering2


def test_version_exists():
    assert hasattr(pytest_ordering2, '__version__')


def test_version_valid():
    assert re.match(r'[0-9]+\.[0-9]+(\.[0-9]+)?$',
                    pytest_ordering2.__version__)
