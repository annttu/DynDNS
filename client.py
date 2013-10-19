#!/usr/bin/env python
# encoding: utf-8

"""
Simple DynDNS script
"""

__author__ = 'Antti Jaakkola'
__version__ = '0.0.1'
__email__ = 'annttu@dyndns.annttu.fi'

import dnsutils
import settings
import sys
import logging

logging.basicConfig()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def doUpdate(Client, TTL, Type, Target):
        dnsutils.doUpdate(settings.server, settings.keyfile, settings.origin, False, 'update', TTL, Type, Client ,Target)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: client ttl type target")
        sys.exit(1)
    doUpdate(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
