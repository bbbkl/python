# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: BaseItem.py
#
# description
"""\n\n
    Base class for activity, ...
"""

from command_mapper import CommandMapper
import re

class BaseItem(object):
    """Base item which holds tokens and command"""
    
    mode_51 = False # swith for 5.1 or 5.2/5.3 mode
    class_description_mismatches = {}
    
    def __init__(self, tokens, command):
        self._tokens = tokens
        self._command = command
      
    @classmethod  
    def to_float(cls, string):
        """convert to float"""
        return float(string.replace(',', '.'))    
        
    @classmethod
    def make_key(cls, *parts):
        """generic key generator"""
        key = str(parts[0])
        for part in parts[1:]:
            key += "_%s" % part # use _ as delimiter
        return key
    
    @classmethod
    def set_mode51(cls):
        """switch on 5.1 mode"""
        cls.mode_51 = True
        
    @classmethod
    def mode51(cls):
        """either mode 5.1 or 5.2/5.3/6.1"""
        return cls.mode_51
        
    @classmethod 
    def cmd_ids(cls):
        """get command ids of given class"""
        ids = []
        for command in cls.commands():
            ids.append(CommandMapper.text2num()[command])
        return ids
    
    def token_descriptions(self):
        """get token descritpions"""
        return []
    
    def class_name(self):
        """get class name"""
        return self.__class__.__name__
    
    @classmethod 
    def format_output(cls, descriptions, tokens, with_index_numbers):
        """pretty print description line"""
        line = ""
        cnt = len(tokens)
        if with_index_numbers and len(descriptions) < cnt:
            diff = cnt - len(descriptions)
            for i in range(diff):
                descriptions.append("xxx_missing_description")
        if cnt < 4:
            for i in range(cnt):
                line += "\t%s=%s" % (descriptions[i], tokens[i])
            return line
        if with_index_numbers:
            max_len = max(map(len, descriptions)) + 3
            fmt = "\n\t%%2d %%-%ds %%s" % max_len
            for i in range(cnt):
                line += fmt % (i+1, descriptions[i], tokens[i])
        else:
            max_len = max(map(len, descriptions))
            fmt = "\n\t%%-%ds %%s" % max_len
            for i in range(cnt):
                line += fmt % (descriptions[i], tokens[i])
        return line
            
    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        return self._tokens
    
    def verbose_token(self, pos, fct, tokens):       
        """check wether given pos is available and call fct with tokens[pos]"""
        if len(tokens) > pos:
            val = tokens[pos]
            stringified_val = fct(val)
            if stringified_val:
                tokens[pos] = "%s (%s)" % (val, stringified_val)
        
    def headline_ids(self):
        """return most significant ids"""
        return None
            
    def headline(self):
        """line with class name and most significant ids"""
        text = self.class_name()
        ids = self.headline_ids()
        if ids is not None:
            text += "\t%s" % ids
        return text
    
    @classmethod 
    def format_check(cls, tokens, descriptions):
        """check that a special field fits expected format"""
        checks = {'process_area' : '(""|[A-Z]{3})'}
        for key in checks:
            if key in descriptions:
                pos = descriptions.index(key)
                if pos > len(tokens):
                    continue
                token = tokens[pos]
                if not re.match(checks[key], token):
                    classname = cls.__name__
                    print("\nERROR bad line of %s, %s='%s' does not fit format '%s', line='%s'" % \
                          (classname, key, token, checks[key], '\t'.join(tokens)))
                    return 0
        return 1
    
    @classmethod 
    def check_descriptions_tokens_mismatch(cls, descriptions, tokens):
        """warn about a token / description length mismatch one"""
        if not cls.format_check(tokens, descriptions):
            return
        
        diff = len(descriptions) - len(tokens)
        if diff == 0:
            return
        classname = cls.__name__
        if classname in cls.class_description_mismatches and \
           diff == cls.class_description_mismatches[classname]:
            return # we know about this mismatch already
        cls.class_description_mismatches[classname] = diff
        
        msg = "\n%s - Description/Token mismatch for class: %s" % ("Warning" if diff>0 else "ERROR", classname)
        msg += ", mode: %s\n" % ("5.1" if cls.mode51() else ">=5.2")
        msg += "#description: %d, #tokens: %d\n" % (len(descriptions), len(tokens))
        #msg += "line=%s" % "\t".join(tokens)
        if diff > 0:
            msg += "ignored descriptions: %s" % descriptions[-diff:] 
        print(msg)
            
    def line_with_description(self, with_index_numbers):
        """combine values with description"""
        descriptions = self.token_descriptions()
        self.check_descriptions_tokens_mismatch(descriptions, self._tokens)
        tokens = self.verbose_tokens()
        line = '%s %s' % (self.headline(), self.format_output(descriptions, tokens, with_index_numbers))
        return line
