
from flask_sqlalchemy.pagination import Pagination

from badger.extension import MyJsonConvertable
from badger.error import *

import functools

# def badger_Response(_func=None, *, parameter=None):


def badger_Response(_func=None, *, debug: bool = False):
    """Badger response decorator

    converts the functions return valuse to the API response structure.\n
    The decorated function can return a single `item` or a `tuple`.\n

    The return tuple can have following parameters:\n
    (`item`, `status_code`, `page_info`)\n
    These parameters must be set in this order, only following ones can be omitted.\n
    For example to only set `item` and `page_info` the return tuple must be `(item, None, page_info_instance)`
    \n
    `item`
    ------
    must be of type:\n
        `flask_sqlalchemy.pagination.Pagination` or\n
        `list[MyJsonConvertable | dict | str]` or \n
        `MyJsonConvertable`, `str`, `dict`\n

    `status_code`
    -------------
    status_code must be a `int` or `None` for default.\n
    is used as the HTTP status code, default is '200'\n

    `page_info`
    -------------
    must be of type `API_Response_Handler.API_page_info` or `None`\n
    use `API_Response_Handler.create_page_info(page: Pagination)` to get `API_page_info` instance
    if `None` page_info is auto generated from `item`



    """
    def badger_Response_decorator(func):
        @functools.wraps(func)
        def handle_response(*args, **kwargs):
            return_items = []
            errors = []
            status_code = None  # http status code
            page_info = None

            try:
                item = func(*args, **kwargs)

                if isinstance(item, tuple):
                    page_info = item[2] if len(item) >= 3 else None
                    status_code = item[1] if len(item) >= 2 else None
                    item = item[0]

                # if item is None:
                #     raise BadgerEntryNotFound("No matching entry found")

                if isinstance(item, list):
                    return_items.extend(item)
                elif isinstance(item, Pagination):
                    return_items = item
                else:
                    return_items.append(item)

            except BadgerBaseException as e:
                errors.append(e)

            if debug:
                print("return_items", return_items)
                print("errors", errors)

            return API_Response_Handler(items=return_items, errors=errors, status_code=status_code, page_info=page_info).get_response()

        return handle_response

    if _func is None:
        return badger_Response_decorator
    else:
        return badger_Response_decorator(_func)


class API_Response_Handler():

    class API_page_info():
        totalResults: int
        resultsPerPage: int

        totalPages: int
        curPageID: int = None
        nextPageID: int = None
        prevPageID: int = None

        def __init__(self, page: Pagination = None) -> None:
            if page is not None:
                self.totalResults = page.total
                self.resultsPerPage = page.per_page
                self.totalPages = page.pages

                self.curPageID = page.page
                self.nextPageID = page.next_num
                self.prevPageID = min(page.prev_num, self.totalPages) if page.has_prev else None

        def to_json(self) -> dict:
            json = {
                "totalResults": self.totalResults,
                "resultsPerPage": self.resultsPerPage,
                "totalPages": self.totalPages,
            }

            if self.curPageID:
                json["curPageID"] = self.curPageID
            
            if self.nextPageID:
                json["nextPageID"] = self.nextPageID

            if self.prevPageID:
                json["prevPageID"] = self.prevPageID

            return json

    status_code = 200  # HTTP status code

    items = []
    page_info: API_page_info = None
    # warnings = []
    errors = []

    def __init__(self,
                 items: list[MyJsonConvertable | dict] | Pagination = None,
                 errors: list[BadgerBaseException] = None,
                 status_code: int = None,
                 page_info: API_page_info = None
                 ) -> None:

        self.items = items
        self.errors = errors

        if status_code is not None:
            self.status_code = status_code

        if page_info is not None:
            self.page_info = page_info

    def get_response(self) -> (dict, int):
        """Returns a response dict and status code
        """
        response_obj = {
            # "items": None,
            # "warnings": None, # TODO
            # "errors": None,
        }

        # status_code = 200

        errors = self._handle_data(data=self.errors)

        if errors is None or len(errors) < 1:
            self._items = self._handle_data(data=self.items)
            response_obj["items"] = self._items

            # handle page_info
            page_info = self._handle_page_info()
            response_obj["pageInfo"] = page_info.to_json()

            print("DEBUG page num results: ", len(response_obj["items"]))
        else:
            print("DEBUG error: ", self.errors)
            response_obj["errors"] = errors
            self.status_code = self._get_status_code(self.errors)

        return (response_obj, self.status_code)

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

    ####################################################################################################
    # Return items handler
    ####################################################################################################
    def _handle_data(self, data: list[MyJsonConvertable | dict] | Pagination) -> list | None:
        """Convert data to list of dicts
        """

        # print()
        # print("DEBUG DATA: ", data)
        # print("DEBUG DATA: ", type(data))
        # print()

        if data is None:
            return None

        data_list = None

        if isinstance(data, list):
            data_list = self._handle_items_list(items=data)

        elif isinstance(data, Pagination):
            data_list = self._handle_page(page=data)

        elif isinstance(data, MyJsonConvertable):
            raise NotImplementedError("no longer works this way")
            data_list = _handel_itme(data_list, data)

        else:
            raise TypeError("Unsupported data type")

        return data_list
        # return data_list if len(data_list) > 0 else None

    def _handle_items_list(self, items: list[MyJsonConvertable | dict]):
        item_list = []
        for item in items:
            item_list = self._handel_item(item_list, item)

        return item_list

    def _handle_page(self, page: Pagination) -> list | None:
        self.page_info = self.API_page_info(page=page)

        item_list = []
        for item in page.items:
            item_list = self._handel_item(item_list, item)

        return item_list

    def _handel_item(self, list, data: MyJsonConvertable | dict) -> list:
        """
        convert item and add to list
        creates list if non exists
        """
        if list is None:
            list = []

        # print()
        # print("DEBUG CONVERT: ", data)
        # print("DEBUG CONVERT: ", type(data))
        # print("DEBUG CONVERT: ", isinstance(data, Pagination))
        # print("DEBUG CONVERT: ", isinstance(data, QueryPagination))
        # print()

        if data is None:
            return list

        if isinstance(data, dict) or isinstance(data, str):
            item = data

        elif isinstance(data, MyJsonConvertable):
            item = data.to_dict()
            # item["__class__"] = data.__class__.__name__

        else:
            raise TypeError(
                f"Must be of type MyJsonConvertable, dict or str, got: {type(data)}")

        list.append(item)
        return list

    ##################################################
    ##################################################
    def _handle_page_info(self):
        page_info = self.page_info

        if page_info is None:
            page_info = self.API_page_info()
            num_item = len(self._items)
            page_info.totalPages = 1
            page_info.resultsPerPage = num_item
            page_info.totalResults = num_item

        return page_info

    def _get_status_code(self, errors: list[BadgerBaseException]):
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

    @classmethod
    def create_page_info(cls, page: Pagination) -> API_page_info:
        page_info = cls.API_page_info(page=page)
        return page_info
