
import json
from badger.extension import MyJsonConvertable

__all__ = ["BadgerException"]


class BadgerErrorCode():
    ERROR = 18_200


class BadgerException(Exception, MyJsonConvertable):
    error_code = None
    error_message = None

    def __init__(self, error_code: BadgerErrorCode, message: str) -> None:
        self.error_code = error_code
        self.error_message = message

    def to_dict(self):
        return {
            "error_code": int(self.error_code),
            "error_message": self.error_message
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return (
            f"error_code={self.error_code},message={self.error_message}"
        )

    def __str__(self):
        return self.__repr__()
