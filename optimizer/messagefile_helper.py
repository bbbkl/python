# -*- coding: UTF-8 # Encoding declaration -*-
# file: messagefile_helper.py
#
# description
"""\n\n
    script to truncate messagefile to opti/sync and to inline necessary config entries
"""

# import ...
from argparse import ArgumentParser
import re
import os
import glob

VERSION = '0.1'


class ConfigEntry:

    def __init__(self, config_key):
        self.acm_key = None
        self.key = None
        self.acmvalue = None
        self.cfgvalue = None
        if config_key.startswith('PP_'):
            self.acm_key = config_key
        else:
            self.key = config_key

    def get_key(self, with_pp_prefix=False):
        if self.key is not None and not self.equal_value():
            return "PP_" + self.key if with_pp_prefix else self.key
        return self.acm_key

    def get_value(self):
        if self.get_cfgvalue() is not None:
            return self.get_cfgvalue()
        return self.get_acmvalue()

    def add_acm_info(self, key, value):
        self.acm_key = key
        self.acmvalue = value

    def add_info(self, key, value):
        self.key = key
        self.cfgvalue = value

    def get_acmvalue(self):
        if self.acmvalue == "YES":
            return "1"
        elif self.acmvalue == "NO":
            return "0"
        return self.acmvalue

    def get_cfgvalue(self):
        return self.cfgvalue

    def is_relevant(self):
        if self.make_id(self.get_key()) in self.unwanted():
            return False
        return True

    def equal_value(self):
        return self.get_acmvalue() == self.get_cfgvalue()

    def is_acm_only(self):
        return self.key is None

    def __str__(self):
        return "%s=%s val=%s acm_val=%s is_relevant=%d" % \
               (self.get_key(), self.get_value(), self.get_cfgvalue(), self.get_acmvalue(), int(self.is_relevant()))

    @classmethod
    def make_id(cls, id_candidate):
        if id_candidate.startswith('PP_'):
            return id_candidate.upper()
        return "PP_%s" % id_candidate.upper()

    @classmethod
    def unwanted(cls):
        keys = ["ERPCODEPAGE", "FILENAMEPREFIX", "MESSAGEFILETIMESTAMP", "MESSAGEFILEWRITE",
                "SENDSOLUTIONASYNC", "SKIPSENDINGPLANNINGINFO", "RESTARTTIME", "DEBUGLEVELLOGFILE"]
        return map(lambda key: ConfigEntry.make_id(key), keys)


class ReasonConfigEntry(ConfigEntry):
    def __init__(self, key):
        # print("xxx SPECIAL ReasonConfigEntry constructor called xxx")
        super().__init__(key)

    def get_acmvalue(self):
        if self.acmvalue == '':
            return '0'
        if self.acmvalue == '2':
            return '1'
        return super().get_acmvalue()


def config_entry_factory(new_id, entries):
    if new_id not in entries:
        if new_id == "PP_OPTIMIZATIONREASONDETERMINATION":
            new_entry = ReasonConfigEntry(new_id)
            entries[new_id] = new_entry
        else:
            new_entry = ConfigEntry(new_id)
            entries[new_id] = new_entry
    return entries[new_id]


def get_configentries(message_file):
    config_entries = {}
    rgx = re.compile('^([^=]*)=(.*)$')
    rgx_acm = re.compile(r'^3\t(PP_\S+)\t(.*)$')
    cfg_start = cfg_end = False
    with open(message_file) as readfile:
        for line in readfile:
            if cfg_end:
                hit = rgx_acm.search(line)
                if hit:
                    key = ConfigEntry.make_id(hit.group(1))
                    entry = config_entry_factory(key, config_entries)
                    entry.add_acm_info(hit.group(1), hit.group(2))
            elif cfg_start:
                hit = rgx.search(line)
                if hit:
                    key = ConfigEntry.make_id(hit.group(1))
                    entry = config_entry_factory(key, config_entries)
                    entry.add_info(hit.group(1), hit.group(2))
                cfg_end = line.startswith("End-Config")
            else:
                cfg_start = line.startswith("Start-Config")
    return config_entries


def inline_get_borders(message_file):
    border1 = -1
    border2 = -1
    with open(message_file) as readfile:
        for idx, line in enumerate(readfile):
            if border1 == -1 and line.startswith("2\t111"):
                border1 = idx - 2
            elif line.endswith("2\t199\n"):
                border2 = idx
                break
    return border1, border2


def inline_config(message_file, entries):
    """
    # 1. Orders rausschreiben als block
    # 2. Start index, Ende index
    # 3. Neue Datei, bis startindex rauschreiben, orderblock, endeindex  (enumerate ist gut)
    """
    message_file_tmp = message_file + "_tmp"
    idx1, idx2 = inline_get_borders(message_file)
    with open(message_file_tmp, "w") as writefile:
        with open(message_file) as readfile:
            for idx, line in enumerate(readfile):
                if idx == idx2:
                    for entry in filter(lambda x: x.is_relevant(), entries.values()):
                        writefile.write("3\t%s\t%s\n2\t111\n" % (entry.get_key(True), entry.get_value()))
                if idx <= idx1 or idx >= idx2:
                    writefile.write(line)
    os.unlink(message_file)
    os.rename(message_file_tmp, message_file)


def pretty_print_config(config_entries):
    entries = config_entries.values()
    print("important:")
    for entry in filter(lambda x: x.is_relevant() and not x.is_acm_only() and not x.equal_value(), entries):
        print("\t%s" % entry)

    print("\nacm_only:")
    for entry in filter(lambda x: x.is_relevant() and x.is_acm_only(), entries):
        print("\t%s" % entry)

    print("\nirrelevant:")
    for entry in filter(lambda x: not x.is_relevant(), entries):
        print("\t%s" % entry)


def checkopt_line(line):
    if line.find('120') != -1 or line.find('196') != -1:
        hit = re.search('^2\t(120|196)($|\t)', line)
        if hit:
            return 'opti' if hit.group(1) == '120' else 'sync'
    return None


def checkopt(message_file):
    with open(message_file) as searchfile:
        for line in searchfile:
            res = checkopt_line(line)
            if res is not None:
                return res
    return 'unknown'


def checkdate_line(line, longdate):
    hit = re.search(r'^3\t(\d{2})\.(\d{2})\.(\d{4})\t(\d{2}):(\d{2})', line)
    if hit:
        if longdate:
            my_year = hit.group(3)
            my_month = hit.group(2)
            my_dd = hit.group(1)
            my_hh = hit.group(4)
            my_min = hit.group(5)
            return my_year + my_month + my_dd + '_' + my_hh + my_min
        else:
            my_mm = hit.group(2)
            my_dd = hit.group(1)
            return my_mm + my_dd
    return None


def checkdate(message_file, longdate):
    # 23.08.2022	03:02
    with open(message_file) as searchfile:
        for line in searchfile:
            date = checkdate_line(line, longdate)
            if date is not None:
                return date
    return ''


def get_compacted_filename(message_file, prefix, longdate):
    what = checkopt(message_file)
    date = checkdate(message_file, longdate)
    if prefix == '':
        prefix = os.path.splitext(message_file)[0]
    what = "" if what == "opti" else '.' + what
    return prefix + '_' + date + what + '.dat'


def get_destination_path(src_filename, prefix, longdate):
    new_name = get_compacted_filename(src_filename, prefix, longdate)
    return os.path.join(os.path.dirname(src_filename), new_name)


def is_num_only_line(line):
    return re.match(r'^\d+$', line)


def write_compact_file(src_path, dst_path):
    first_line = 1
    last_4 = None
    rgx_4 = re.compile(r'^4\t(\d+)')
    rgx_stop = re.compile(r'^4\t-')
    with open("%s" % src_path) as openfile:
        with open(dst_path, "w") as copyfile:
            for line in openfile:
                if first_line:
                    first_line = 0
                    if is_num_only_line(line):
                        continue
                copyfile.write(line)
                if len(line) > 0 and line[0] == '4':
                    if rgx_stop.search(line):
                        break
                    hit = rgx_4.search(line)
                    if hit:
                        last_4 = int(hit.group(1))
            # repair opti end and ensure command 130
            if line and line.find('2\t120') != -1:
                copyfile.write('2\t130\n')
                if last_4 is not None:
                    copyfile.write('4\t-%d\n' % (last_4+1))
                print("repaired end of opti")


def check_pegging(fn_old, fn_new):
    """rename pegging.csv file with timestamp, which belongs to a message file"""
    hit = re.search(r'(_\d{8}_\d{6})\.', os.path.basename(fn_old))
    if hit:
        timestamp = hit.group(1)
        csv_files = glob.glob(os.path.dirname(fn_old) + '/*' + timestamp + '.pegging.csv')
        if len(csv_files) == 1:
            csv_old = csv_files[0]
            name_new = os.path.splitext(os.path.basename(fn_new))[0] + ".pegging.csv"
            csv_new = os.path.join(os.path.dirname(fn_new), name_new)
            os.rename(csv_old, csv_new)

def cleanup(src, dst, dst_tmp):
    """remove src, rename dst_tmp to dst"""
    os.remove(src)
    if os.path.exists(dst):
        base = dst[:-4]
        idx = 0
        while os.path.exists(dst):
            dst = "%s%02d%s" % (base, idx, dst[-4:])
            idx += 1
    os.rename(dst_tmp, dst)


def handle_file(src_path, prefix, longdate, inline):
    dst_path = get_destination_path(src_path, prefix, longdate)
    dst_tmp = dst_path + ".tmp"
    write_compact_file(src_path, dst_tmp)
    if inline:
        config_entries = get_configentries(dst_tmp)
        inline_config(dst_tmp, config_entries)
    cleanup(src_path, dst_path, dst_tmp)
    print("handled %s" % src_path)
    return dst_path


def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-i', dest='inline', help='inline mode', default=False, action='store_true')
    parser.add_argument('-sc', dest='show_config', default=False, help='show config and exit', action='store_true')
    parser.add_argument('-b', dest='batch_mode', default=False, help='execute in batch mode', action='store_true')
    parser.add_argument('-l', dest='longdate', default=False, help='longdate mode', action='store_true')
    parser.add_argument('-p', '--prefix', metavar='string',  # or stare_false
                        dest="prefix", default='',  # negative store value
                        help="prefix name of shortened message files")

    return parser.parse_args()


def main():
    """main function"""
    args = parse_arguments()
    src_path = args.message_file
    prefix = args.prefix
    longdate = args.longdate
    inline = args.inline

    if args.show_config:
        config_entries = get_configentries(src_path)
        pretty_print_config(config_entries)
        return 0

    # either bach mode or single file
    files_to_handle = [src_path, ]
    if args.batch_mode:
        files_to_handle = glob.glob(src_path + '/*.dat', recursive=False)

    for fn in files_to_handle:
        new_fn = handle_file(fn, prefix, longdate, inline)
        check_pegging(fn, new_fn)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
