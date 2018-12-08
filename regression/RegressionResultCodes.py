# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionResultCodes.py
#
# description
"""\n\n
    result codes for regression programs
"""
from enum import IntEnum

class Regr(IntEnum):
    OK = 0
    DIFF = 1
    FAILED = 2
    FATAL_ERROR = 3
    