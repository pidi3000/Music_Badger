
from badger.extension import MyJsonConvertable
from badger.error import *


class API_Response_Handler():

    @classmethod
    def construct_response_obj(cls, items: MyJsonConvertable | list[MyJsonConvertable] = None, errors: BadgerException | list[BadgerException] = None):
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
    def _handle_data(cls, data: MyJsonConvertable | list[MyJsonConvertable]) -> list | None:
        if data is None:
            return None

        def convert_add(list, data: MyJsonConvertable) -> list:
            """
            conver item and add to list
            creates list if non exists
            """
            if list is None:
                list = []

            item = data.to_dict()
            item["__class__"] = data.__class__.__name__

            list.append(item)
            return list

        data_list = None
        if isinstance(data, list):
            if len(data) > 0:
                for d in data:
                    data_list = convert_add(data_list, d)

        elif isinstance(data, MyJsonConvertable):
            data_list = convert_add(data_list, data)

        else:
            raise TypeError("Unsupported data type")

        return data_list
