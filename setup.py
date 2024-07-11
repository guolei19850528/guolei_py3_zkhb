#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="guolei-py3-zkhb",
    version="0.0.4",
    description="中科华博 API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guolei19850528/guolei_py3_zkhb",
    author="guolei",
    author_email="174000902@qq.com",
    license="MIT",
    keywors=["中科华博", "zkhb"],
    packages=setuptools.find_packages('./'),
    install_requires=[
        "guolei-py3-requests",
    ],
    python_requires='>=3.0',
    zip_safe=False
)
