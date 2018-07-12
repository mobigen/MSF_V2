import sys
import os
import ConfigParser

from secureconfig import SecureConfig

class SConfigParser:
    def __init__(self):
        self.cfg = None

    def read(self, path, keypath):
        f = open(keypath, 'r')
        key = f.read()
        f.close()
        self.cfg = SecureConfig.from_key(key, filepath=path)

    def get(self, section, param):
        return self.cfg.get(section, param.lower())

    def sections(self):
        return self.cfg.sections()

    def getint(self, section, item_key):
        return int(self.cfg.get(section, item_key.lower()))

    def getboolean(self, section, item_key):
        return bool(self.cfg.get(section, item_key.lower()))

    def has_section(self, section):
        return (section in self.cfg.sections())

    def has_option(self, section, item_key):
        try:
            return bool(self.getboolean(section, item_key))
        except KeyError:
            return False


def write(sconf, path):
    fh = open(path, 'w')
    sconf.write(fh)
    fh.close()

def read(path):
    fr = open(path, 'r')
    data = fr.read()
    fr.close()
    return data

def gen_encrypted_config(key_path, conf_path):
    sconf = SecureConfig.from_key(read(key_path))
    conf = ConfigParser.ConfigParser()
    conf.read(conf_path)

    for section in conf.sections():
        sconf.add_section(section)
        for item_key, item_value in conf.items(section):
            sconf.set(section, item_key, item_value)

    return sconf


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage : %s <Key> <ConfigFilePath> <WritePath>' % sys.argv[0]
        sys.exit()
    key, conf_path, write_path = sys.argv[1:]

    write(gen_encrypted_config(key, conf_path), write_path)

