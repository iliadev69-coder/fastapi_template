from ipaddress import ip_address
from typing import cast

from fastapi import Request
from fastapi.datastructures import Address

from app.core.types import AnyIPAddress


def get_host(request: Request) -> AnyIPAddress:
    if 'X-Forwarded-For' in request.headers:
        ip = ip_address(request.headers['X-Forwarded-For'].split(',')[0])
    elif 'Remote-Addr' in request.headers:
        ip = ip_address(request.headers['Remote-Addr'])
    else:
        ip = ip_address(cast(Address, request.client).host)
    return ip
