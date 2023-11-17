#!/usr/bin/env python

from setuptools import setup
import os

__here__ = os.path.abspath(os.path.dirname(__file__))

from pytest_order import __version__

with open(os.path.join(__here__, "README.md")) as f:
    LONG_DESCRIPTION = f.read()


setup(
    name="pytest-order",
    description="pytest plugin to run your tests in a specific order",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    version=__version__,
    author="mrbean-bremen",
    author_email="hansemrbean@googlemail.com",
    url="https://github.com/pytest-dev/pytest-order",
    packages=["pytest_order"],
    license="MIT",
    entry_points={
        "pytest11": [
            "pytest_order = pytest_order.plugin",
        ]
    },
    python_requires=">=3.6",
    install_requires=[
        "pytest>=5.0; python_version < '3.10'",
        "pytest>=6.2.4; python_version >= '3.10'",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
