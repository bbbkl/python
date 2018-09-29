# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: unhandled.py
#
# description
"""\n\n
    unhandled message commands class
"""

from message.baseitem import BaseItem

class Unhandled(BaseItem):
    """unhandled message ids"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod        
    def commands(cls):
        return []  