# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionException.py
#
# description
"""\n\n
    base exception class for regression
"""

class RegressionException(Exception):
    """base exception class of regression"""
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

class RegressionReasonException(RegressionException):
    pass