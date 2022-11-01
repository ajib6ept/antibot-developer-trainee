import ipaddress

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

_TIME_SETTINGS = {"s": 1, "m": 60, "h": 60 * 60}

DEFAULT_IP = "127.0.0.1"


def get_subnet_from_headers(request, ipv4_mask):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(",")[-1].strip()
    else:
        ip_addr = DEFAULT_IP

    subnet = ipaddress.ip_network(
        f"{ip_addr}/{ipv4_mask}", strict=False
    ).network_address
    return str(subnet)


class RatelimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            ipv4_mask = settings.RATELIMIT_IPV4_MASK
            limit = settings.RATELIMIT_LIMIT
            block = settings.RATELIMIT_BLOCK
            pref = settings.RATELIMIT_CACHE_PREFIX
        except AttributeError:
            pass
        try:
            block_time = int(block[:-1]) * _TIME_SETTINGS[block[-1]]
            limit_req = int(limit.split("/")[0])
            limit_ttl = _TIME_SETTINGS[limit.split("/")[1]]
        except IndexError:
            pass

        subnet = get_subnet_from_headers(request, ipv4_mask)
        key = pref + subnet

        if cache.get(f"{key}+ban"):
            return HttpResponse(status=429)

        added = cache.add(key, 1, timeout=limit_ttl)
        if not added:
            cache.incr(key)
        value = cache.get(key)
        if value >= limit_req:
            cache.set(f"{key}+ban", value=1, timeout=block_time)

        return self.get_response(request)
