from ipaddress import IPv4Address, IPv6Address
from typing import Annotated

from pydantic import PlainSerializer

AnyIPAddress = Annotated[IPv4Address | IPv6Address, PlainSerializer(str, return_type=str)]
