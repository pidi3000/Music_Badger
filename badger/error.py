
import json
from badger.extension import MyJsonConvertable

__all__ = [
    "BadgerBaseException", "BadgerEntryNotFound", "BadgerYTUserNotAuthorized"
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

    # def to_json(self):
    #     return json.dumps(self.to_dict())

    def __repr__(self):
        return (
            f"status_code={self.status_code}, error_type={self.error_type}, message={self.error_message}"
        )

    def __str__(self):
        return self.__repr__()


####################################################################################################
# Public Badger Exceptions
####################################################################################################
class BadgerMisingParameter(BadgerBaseException):
    def __init__(self, message: str = "One of the requiered parameters is missing", status_code=400) -> None:
        super().__init__(message, error_type="MissingParameter", status_code=status_code)


class BadgerYTUserNotAuthorized(BadgerBaseException):
    def __init__(self, message: str = "Service not authorized on users YouTube Account", status_code=403) -> None:
        super().__init__(message, error_type="YTUserNotAuthorized", status_code=status_code)


class BadgerEntryNotFound(BadgerBaseException):
    def __init__(self, message: str = "Requested resource could not be found", status_code=404) -> None:
        super().__init__(message, error_type="EntryNotFound", status_code=status_code)


class BadgerUnsupportedMediaType(BadgerBaseException):
    def __init__(self, message: str = "The media type sent is not supported", status_code=415) -> None:
        super().__init__(message, error_type="UnsupportedMediaType", status_code=status_code)


####################################################################################################
# Private Badger Exceptions
####################################################################################################
class BadgerPrivateBaseException(BadgerBaseException):
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
        super().__init__(message, status_code, error_type)

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "type": "InternalServerError",
            "message": "Server encounter an internal error. Try again later. Admin check logs"
        }

    def __repr__(self):
        return (
            f"status_code={self.status_code}, error_type={self.error_type}, message={self.error_message}"
        )


class Badger_YT_API_key_not_found(BadgerPrivateBaseException):
    def __init__(self, message: str = "YT_API_KEY must be set in settings to use API", status_code=500) -> None:
        super().__init__(message, error_type="API-KeyNotFound", status_code=status_code)
