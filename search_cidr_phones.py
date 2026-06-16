import ipaddress
import sys


def valid_phone_prefix(phone: int) -> bool:
    ds = [int(c) for c in str(phone)]  # digits
    return (
        ds[0] >= 2  # 0/1...
        and (len(ds) < 3 or ds[1] != 1 or ds[2] != 1)  # X11...
        and (len(ds) <= 3 or ds[3] >= 2)  # (XXX) 0/1...
        and (len(ds) < 6 or ds[4] != 1 and ds[5] != 1)  # (XXX) X11...
    )


def phone_prefixes(cidr):
    lo = int(cidr.network_address)
    hi = int(cidr.broadcast_address)
    x = max(lo, 200_000_0000)
    prefixes = []
    while x <= hi:
        k = 1
        while x % (k * 10) == 0 and x + (k * 10) - 1 <= hi:
            k *= 10
        prefix = x // k
        if valid_phone_prefix(prefix):
            prefixes.append(prefix)
        else:
            print("rejected prefix", prefix, file=sys.stderr)
        x += k
    return prefixes


for line in sys.stdin:
    cidr = ipaddress.ip_network(line.strip())
    for prefix in phone_prefixes(cidr):
        print(prefix)
