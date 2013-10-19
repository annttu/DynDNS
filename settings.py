# encoding: utf-8

"""
Settings file for dyndns.py
"""

server='localhost'
keyfile='tsig.key'
origin='example.com'

# Remember tailing dot!
clients = {
    # Format: 'secret', 'client1.example.com.',
    'AiNg4QuikoosuV5aith0ahnuc': 'client1.example.com.',  # client1.example.com can be updated using secret AiNg4QuikoosuV5aith0ahnuc
}

try:
    from settings_local import *
except ImportError:
    pass
