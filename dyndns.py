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
import traceback
import utils
import logging

import urlparse
from cgi import escape
from flup.server.fcgi import WSGIServer

debugging=False

logger = logging.getLogger('dyndns')
if settings.logfile:
    hdlr = logging.FileHandler(settings.logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

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
                if 'ip' in GET and len(GET['ip']) == 1:
                    addr = GET['ip'][0].strip()
                if not utils.check_ipv4(addr):
                    errors = "Only IPv4 currently supported!"
                    status = "503 Service Unavailable"
                if not errors:
                    try:
                        old = socket.gethostbyname(client)
                        dnsutils.doUpdate(settings.server, settings.keyfile, settings.origin, False, 'delete', '360', 'A', client, old)
                        logger.info("Deleted old entry %s IN A 360 %s" % (client, old))
                    except socket.gaierror:
                        # address not set
                        pass
                    except dnsutils.DynDNSException as e:
                        logger.exception(e)
                        errors = "%s: %s" % (str(e), traceback.format_exc())
                        status = '503 Service Unavailable'
                    except Exception as e:
                        logger.exception(e)
                        errors = "%s: %s" % (str(e) or type(e), traceback.format_exc())
                        status = '503 Service Unavailable'
                if not errors:
                    try:
                        dnsutils.doUpdate(settings.server, settings.keyfile, settings.origin, False, 'update', '360', 'A', client, addr)
                        status = '200 OK'
                        logger.info("Added new entry %s IN A 360 %s" % (client, addr))
                    except dnsutils.DynDNSException as e:
                        logger.exception(e)
                        errors = "%s: %s" % (str(e) or type(e), traceback.format_exc())
                        status = '503 Service Unavailable'
                    except Exception as e:
                        logger.exception(e)
                        errors = "%s: %s" % (str(e) or type(e), traceback.format_exc())
                        status = '503 Service Unavailable'
    start_response(status, [('Content-Type', 'text/plain')])
    yield(status)
    yield("\n")
    if debugging:
        yield("%s" % errors)
        yield("\n")

def run(debug=False):
    global debugging
    debugging = debug
    if debug:
        logger.setLevel(logging.DEBUG)
    WSGIServer(doUpdate, debug=debug).run()

if __name__ == '__main__':
    #WSGIServer(doUpdate).run()
    run(debug=True)
