# from __future__ import annotations

from re import match
from datetime import datetime
import json

from .extension import MyJsonEncoder


# TODO move this to a better place, but where IDK ¯\_(ツ)_/¯
def exception_to_dict(exception: Exception):
    return {
        "error": {
            "type": str(exception.__class__.__name__),
            "msg": str(exception)}
    }
