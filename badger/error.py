
import json
from badger.extension import MyJsonConvertable

__all__ = [
    "BadgerBaseException", "BadgerEntryNotFound"
]


def handle_server_exception(e):
    from flask import json
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "status_code": e.code,
        "type": e.name,
        "message": e.description
    })
    response.content_type = "application/json"
    return response


####################################################################################################
# Badger Exceptions
####################################################################################################
class BadgerBaseException(Exception, MyJsonConvertable):
    # error_code = None
    status_code = None  # HTTP status code
    error_message: str = None
    error_type: str = None

    def __init__(self, message: str, status_code: int,  error_type: str = None) -> None:
        """
        Parameters
        ----------
        message
            the error message
        error_type
            error type name (EntryNotFound, etc.)
        status_code
            the HTTP status code

        """
        # self.error_code = error_code
        self.error_message = message

        if error_type:
            self.error_type = error_type

        if status_code:
            self.status_code = status_code

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "type": self.error_type,
            "message": self.error_message
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return (
            f"status_code={self.status_code}, error_type={self.error_type}, message={self.error_message}"
        )

    def __str__(self):
        return self.__repr__()


class BadgerUserNotAuthorized(BadgerBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message, error_type="UserNotAuthorized", status_code=400)


class BadgerEntryNotFound(BadgerBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message, error_type="EntryNotFound", status_code=404)
