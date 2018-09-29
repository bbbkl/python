# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: sonic_queues.py
#
# description
"""\n\n
    generate names of sonic queues for given proalpha version
"""

from argparse import ArgumentParser

VERSION = 1.0

def users():
    """list of users which are known as optimizer users"""
    # bk  bernd krueger
    # da
    # dcs
    # doa doris altenberndt
    # fw  frank weiler
    # HN  holger neu
    # jhp jens port
    # lhe
    # mb  markus berg
    # ms
    # fei frank eimer
    # pek peter koehler
    # ub  uwe baumann
    # um  
    # ab
    # kmu kerstin muxfeld
    # rw  robert wagner
    # 
    return ['bk', 'rw', 'JL', 'da', 'dcs', 'DoA', 'fw', 'HN', 'jhp', 'lhe', 'mb', 'ms', 'fei', 'FEi', 'pek', 'ub', 'um', 'ab']

def generate_user_queue_names(pa_version, user):
    to_queue = 'apsMessaging.proalpha-%s-demo-%s.apsdemo.toApsServer' % (pa_version, user)
    from_queue = 'apsMessaging.proalpha-%s-demo-%s.apsdemo.fromApsServer' % (pa_version, user)
    return (to_queue, from_queue)
    
def generate_queue_names(pa_version):
    for user in users():
        to_queue, from_queue = generate_user_queue_names(pa_version, user)
        print(to_queue)
        print(from_queue)
    
def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    
    parser.add_argument('pa_version', metavar='pa_version', help='proalpha version, e.g. 52i')
    return parser.parse_args()
        
def main():
    """main function"""
    args = parse_arguments()
    generate_queue_names(args.pa_version)
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise