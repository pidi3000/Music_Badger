# from __future__ import annotations

import json

from .extension import MyJsonEncoder


# TODO move this to a better place, but where IDK ¯\_(ツ)_/¯
def exception_to_dict(exception: Exception):
    return {
        "error": {
            "type": str(exception.__class__.__name__),
            "msg": str(exception)}
    }

def obj_list_to_json(list) -> dict:
    """Turn a list of custom classes into json serializable dict"""
    return json.loads(json.dumps(list, cls=MyJsonEncoder))