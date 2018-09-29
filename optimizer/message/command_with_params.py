# description
"""\n\n
    commands with params erp -> optimizer 
"""

from message.baseitem import BaseItem
from to_string import ToString

class Command_OptimizeCTP(BaseItem):
    """One material reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def headline_ids(self):
        """get headline for explained mode"""
        return "%d %s" % (self._command.cmd_id(), self._command.text())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        #print("xxx len tokens=%d tokens='%s'" % (len(tokens), str(tokens)))
        self.verbose_token(0, ToString.optimization_type, tokens)
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandoptimizeCTP_________', 'DEF_ERPCommandoptimizeSAP_________' ]

    def token_descriptions(self):
        return ['optimization_type', 'preserve_dynamic_buffer' ]