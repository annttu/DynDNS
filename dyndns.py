#!/usr/bin/env python
# encoding: utf-8

"""
Simple DynDNS script
Provides simple web-interface to update dynamic dns-addresses using 
nsupdate.
"""

__author__ = 'Antti Jaakkola'
__version__ = '0.0.1'
__email__ = 'annttu@dyndns.annttu.fi'

import dnsutils
import settings
import socket

import urlparse
from cgi import escape
from flup.server.fcgi import WSGIServer

## Main view
def doUpdate(environ, start_response):
    status = '403 Forbidden'
    GET = urlparse.parse_qs(environ['QUERY_STRING'])
    addr = environ['REMOTE_ADDR']
    errors = ''
    if 'secret' in GET:
        if len(GET['secret']) == 1:
            if GET['secret'][0] in settings.clients:
                client = settings.clients[GET['secret'][0]]
                try:
                    old = socket.gethostbyname(client)
                    dnsutils.doUpdate(settings.server, settings.keyfile, settings.origin, False, 'delete', '360', 'A', client, old)
                except dnsutils.DynDNSException as e:
                    errors = "%s" % e
                    status = '503 Service Unavailable'
                except Exception as e:
                    errors = "%s" % e
                    status = '503 Service Unavailable'
                try:
                    dnsutils.doUpdate(settings.server, settings.keyfile, settings.origin, False, 'update', '360', 'A', client, addr)
                    status = '200 OK'
                except dnsutils.DynDNSException as e:
                    errors = "%s" % e
                    status = '503 Service Unavailable'
                except Exception as e:
                    errors = "%s" % e
                    status = '503 Service Unavailable'
    start_response(status, [('Content-Type', 'text/plain')])
    #for k, v in environ.items():
    #    if type(v) == str or type(v) == unicode:
    #        yield("%s: %s\n" % (escape(k), escape(v)))
    yield(status)
    yield("\n")
    yield(errors)

if __name__ == '__main__':
    WSGIServer(doUpdate).run()
