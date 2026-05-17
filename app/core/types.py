from app.core.ip_address import AnyIPAddress
from app.schemas.base import Filter, OrFilterGroup

Filters = Filter | OrFilterGroup

__all__ = ('AnyIPAddress', 'Filters')
