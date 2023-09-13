
from badger.extension import MyJsonConvertable
from badger.error import *

import functools

# def badger_Response(_func=None, *, parameter=None):


def badger_Response(_func=None, *, debug: bool = False):
    """Badger response decorator
    
    converts the functions return valuse to the API response structure
    """
    def badger_Response_decorator(func):
        @functools.wraps(func)
        def handle_response(*args, **kwargs):
            return_items = []
            errors = []

            try:
                item = func(*args, **kwargs)

                if item is None:
                    raise BadgerEntryNotFound("No matching entry found")

                if isinstance(item, list):
                    return_items.extend(item)
                else:
                    return_items.append(item)

            except BadgerBaseException as e:
                errors.append(e)

            if debug:
                print("return_items", return_items)
                print("errors", errors)

            return API_Response_Handler(items=return_items, errors=errors).get_response()

        return handle_response

    if _func is None:
        return badger_Response_decorator
    else:
        return badger_Response_decorator(_func)


class API_Response_Handler():
    items = []
    # warnings = []
    errors = []

    def __init__(self, items: list[MyJsonConvertable | dict] = None, errors: list[BadgerBaseException] = None) -> None:
        self.items = items
        self.errors = errors

    def get_response(self) -> (dict, int):
        """Returns a response dict and status code
        """
        response_obj = {
            # "data": None,
            # "warnings": None, # TODO
            # "errors": None,
        }

        status_code = 200

        errors = self._handle_data(data=self.errors)

        if errors is None:
            items = self._handle_data(data=self.items)
            response_obj["items"] = items

        else:
            response_obj["errors"] = errors
            status_code = self._get_status_code(self.errors)

        return (response_obj, status_code)

    @classmethod
    def construct_response_obj(cls, items: list[MyJsonConvertable | dict] = None, errors: list[BadgerBaseException] = None):
        """
        Constructs a response object for API responses

        if `errors` is set response will only contain errors
        """
        response_obj = {
            # "data": None,
            # "warnings": None, # TODO
            # "errors": None,
        }

        response_obj["errors"] = cls._handle_data(data=errors)

        if response_obj["errors"] is None:
            del response_obj["errors"]
            response_obj["items"] = cls._handle_data(data=items)
            # response_obj["warnings"] = cls._handle_data(data=warnings)

        return response_obj

    @classmethod
    def _handle_data(cls, data: list[MyJsonConvertable | dict]) -> list | None:
        """Convert data to list of dicts
        """

        # print()
        # print("DEBUG DATA: ", data)
        # print("DEBUG DATA: ", type(data))
        # print()

        if data is None:
            return None

        def convert_add(list, data: MyJsonConvertable | dict) -> list:
            """
            conver item and add to list
            creates list if non exists
            """
            if list is None:
                list = []

            # print()
            # print("DEBUG CONVERT: ", data)
            # print("DEBUG CONVERT: ", type(data))
            # print()

            if isinstance(data, dict):
                item = data
            elif isinstance(data, MyJsonConvertable):
                item = data.to_dict()
                # item["__class__"] = data.__class__.__name__
            else:
                raise TypeError(
                    f"Must be of type MyJsonConvertable or dict, got: {type(data)}")

            list.append(item)
            return list

        data_list = None
        if isinstance(data, list):
            if len(data) > 0:
                for d in data:
                    if d is not None:
                        data_list = convert_add(data_list, d)

        elif isinstance(data, MyJsonConvertable):
            raise NotImplementedError("no longer works this way")
            data_list = convert_add(data_list, data)

        else:
            raise TypeError("Unsupported data type")

        return data_list
        # return data_list if len(data_list) > 0 else None

    @classmethod
    def _get_status_code(cls, errors: list[BadgerBaseException]):
        status_code: int = 500

        if isinstance(errors, list):
            if len(errors) > 0:
                for error in errors:
                    if error is not None:
                        if error.status_code < status_code:
                            status_code = error.status_code

        elif isinstance(errors, BadgerBaseException):
            raise NotImplementedError("no longer works this way")
            status_code = errors.status_code

        else:
            raise TypeError("Unsupported data type")

        return status_code
