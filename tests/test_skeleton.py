#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from aplatam.skeleton import fib

__author__ = "Dymaxion Labs"
__copyright__ = __author__
__license__ = "new-bsd"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
