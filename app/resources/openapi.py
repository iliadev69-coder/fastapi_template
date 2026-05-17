import operator
from typing import Any, TypedDict, cast

from pydantic import AnyUrl


class OpenAPITag(TypedDict):
    name: str
    description: str


class Contact(TypedDict):
    name: str
    email: str
    url: AnyUrl


app_description: str = 'FastAPI Template'

_openapi_tags: list[OpenAPITag] = [
    OpenAPITag(name='Auth', description='Authentication endpoints.'),
]

_contact: Contact = Contact(
    name='FastAPI Template',
    email='hello@example.com',
    url=AnyUrl('mailto:hello@example.com'),
)

security_schemes = {
    'Bearer': {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'JWT',
        'description': 'JWT bearer token.',
    },
}

openapi_tags = cast(list[dict[str, Any]], sorted(_openapi_tags, key=operator.itemgetter('name')))
contact = cast(dict[str, Any], _contact)
