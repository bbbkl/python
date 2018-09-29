# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionConfig.py
#
# description
"""\n\n
    regression configuration based on a config file
"""

from argparse import ArgumentParser
import re

VERSION = '1.0'

class RegressionConfig:
    """regression configuration based on a configuration file"""
    def __init__(self, configuration_file):
        self.configuration_file = configuration_file
        self.token_map = {}
        self.parse_config()
        self.expand_variables()
        
    def parse_config(self):
        key_map = { 'recipients' : 'recipients=',
                   'src_exe' : 'src_exe=',
                   'regression_exe' : 'regression_exe=',
                   'reference_dir' : 'reference_dir=',
                   'params' : 'params=' }
        
        for line in open(self.configuration_file):
            for key in key_map:
                hit = re.search('^' + key_map[key] + '(.*)', line)
                if hit:
                    del key_map[key]
                    val = hit.group(1)
                    if val.find('#') != -1:
                        val = val[:val.index('#')]
                    val = val.rstrip() 
                    self.token_map[key] = val
                    break
        
        for key in key_map:
            self.token_map[key] = 'MISSING'

    def expand_variables(self):
        for key in self.token_map:
            ref_key = '%' + key + '%'
            for item in self.token_map:
                val = self.token_map[item]
                if val.find(ref_key) != -1:
                    self.token_map[item] = val.replace(ref_key, self.token_map[key])

    def get_val(self, key):
        return self.token_map[key]

    def get_reference_dir(self):
        return self.get_val('reference_dir')
    def get_recipients(self):
        return self.get_val('recipients')
        return self.get_val('reference_dir')
    def get_src_exe(self):
        return self.get_val('src_exe')
    def get_regression_exe(self):
        return self.get_val('regression_exe')
    def get_params(self):
        return self.get_val('params')

    def __str__(self):
        msg = "RegressionConifg '%s'" % self.configuration_file
        for key in sorted(self.token_map):
            msg += '\n\t%s=%s' % (key, self.token_map[key])
        return msg
    

def parse_arguments():
    """parse commandline arguments"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION    
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('config_file', metavar='config_file', help='input regression configuration file')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    config = RegressionConfig(args.config_file)
    print(config)
        
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
