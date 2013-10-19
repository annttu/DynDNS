# encoding: utf-8


"""
DNS library for dyndns script

This file is modifed version of
http://planetfoo.org/files/dnsupdate.py
"""

import dns.query
import dns.tsigkeyring
import dns.update
import dns.reversename
import dns.resolver
import dns.edns
from dns.exception import DNSException, SyntaxError


import logging

logger = logging.getLogger('dns')

class DynDNSException(Exception):
    """
        Pass-through all self made errors
    """
    pass

def getKey(FileName):
    try:
        f = open(FileName)
        key = f.readline()
        f.close()
    except IOError:
        raise DynDNSException('Cannot read key file %s' % FileName)
    k = {key.rsplit(' ')[0]:key.rsplit(' ')[6]}
    try:
        KeyRing = dns.tsigkeyring.from_text(k)
    except:
        raise DynDNSException('%s is not a valid key. The file should be in DNS KEY record format. See dnssec-keygen(8)' % k)
    return KeyRing

def genPTR(Address):
    try:
        a = dns.reversename.from_address(Address)
    except:
        raise DynDNSException('Error: %s is not a valid IP adress' % Address)
    return a

def parseName(Origin, Name):
    try:
        n = dns.name.from_text(Name)
    except:
        DynDNSException('Error: %s is not a valid name' % n)
    if Origin is None:
        Origin = dns.resolver.zone_for_name(n)
        Name = n.relativize(Origin)
        return Origin, Name
    else:
        try:
            Origin = dns.name.from_text(Origin)
        except:
            raise DynDNSException('Error: %s is not a valid origin' % Name)
            exit()
        Name = n - Origin
        return Origin, Name

def doUpdate(Server, KeyFile, Origin, doPTR, Action, TTL, Type, client, target):
    # Get the hostname and the origin
    TTL = dns.ttl.from_text(TTL)
    Origin, Name = parseName(Origin, client)
    # Validate and setup the Key
    KeyRing = getKey(KeyFile)
    # Start constructing the DDNS Query

    # NOTE, due to bug in debian dnspython, keyalgorithm is set as fudge
    Update = dns.update.Update(Origin, keyring=KeyRing)
    # Put the payload together. 
    if Type == 'A' or Type == 'AAAA':
        myPayload = target
        if doPTR == True:
            ptrTarget = Name.to_text() + '.' + Origin.to_text()
            ptrOrigin, ptrName = parseName(None, genPTR(myPayload).to_text())
            ptrUpdate = dns.update.Update(ptrOrigin, keyring=KeyRing)
    elif Type == 'CNAME' or Type == 'NS' or Type == 'TXT' or Type == 'PTR':
        myPayload = target
        do_PTR = False
    else:
        raise DynDNSException("Unknown type %s" % Type)
    # Build the update
    if Action == 'add':
        Update.add(Name, TTL, Type, myPayload)
        if doPTR == True:
            ptrUpdate.add(ptrName, TTL, 'PTR', ptrTarget)
    elif Action == 'delete' or Action == 'del':
        Update.delete(Name, Type, myPayload)
        if doPTR == True:
            ptrUpdate.delete(ptrName, 'PTR', ptrTarget)
    elif Action == 'update':
        Update.replace(Name, TTL, Type, myPayload)
        if doPTR == True:
            ptrUpdate.replace(ptrName, TTL, 'PTR', ptrTarget)
    # Do the update
    try:
        Response = dns.query.tcp(Update, Server)
    except dns.tsig.PeerBadKey:
        raise DynDNSException('ERROR: The server is refusing our key')
    logger.info('Creating %s record for %s resulted in: %s' % (Type, Name, dns.rcode.to_text(Response.rcode())))
    if dns.rcode.to_text(Response.rcode()) != 'NOERROR':
        raise DynDNSException('ERROR: Creating %s record for %s resulted in: %s' % (Type, Name, dns.rcode.to_text(Response.rcode())))
    if doPTR == True:
        try:
            ptrResponse = dns.query.tcp(ptrUpdate, Server)
        except dns.tsig.PeerBadKey:
            raise DynDNSException('ERROR: The server is refusing our key')
        logger.info('Creating PTR record for %s resulted in: %s' % (Name, dns.rcode.to_text(Response.rcode())))
