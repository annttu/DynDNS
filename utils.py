# encoding: utf-8

def check_ipv4(ip):
    if len(ip.split('.')) != 4:
        return False
    for x in ip.split('.'):
        try:
            x = int(x)
            if x < 0 or x > 255:
                return False
        except ValueError:
            return False
    return True
