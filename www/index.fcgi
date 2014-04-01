#!/usr/bin/env python2.6
# encoding: utf-8

import sys

dyndns_path = "/path/to/dyndns/"

sys.path.append(dyndns_path)
execfile('%s/env/bin/activate_this.py' % dyndns_path, dict(__file__='%s/env/bin/activate_this.py' % dyndns_path))

import dyndns as dyndns

if __name__ == '__main__':
    dyndns.run(debug=False)
