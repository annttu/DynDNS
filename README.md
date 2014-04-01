# Dyndns #

Simple dyndns updater.

# Intallation #

Copy www/index.fcgi to somewhere in document root. Update dyndns_path on it.

Install virtualenv if needed.

    virtualenv env
    . env/bin/activate
    pip install -r requirements.txt

Copy settings_local.py.example to settings_local.py and configure it.

# Usage #

    curl http://example.com/dyndns/index.fcgi?secret=myclientsecret
    # or
    curl http://example.com/dyndns/index.fcgi?secret=myclientsecret&ip=1.2.3.4

