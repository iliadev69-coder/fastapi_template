from datetime import datetime
from typing import Annotated

from pydantic import PlainSerializer


def datetime_encoder(dec_value: datetime) -> float:
    return dec_value.timestamp()


timestamp = Annotated[datetime, PlainSerializer(datetime_encoder, return_type=float)]
