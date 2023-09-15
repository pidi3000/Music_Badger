
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask_migrate import Migrate

import json
# from .help_functions import MyJsonEncoder
from json import JSONEncoder
from datetime import datetime


db = SQLAlchemy()
migrate = Migrate()



class MyJsonEncoder(JSONEncoder):
    # https://stackoverflow.com/questions/44146087/pass-user-built-json-encoder-into-flasks-jsonify
    # https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    def default(self, item):
        # print(item.__class__)
        # print(isinstance(o, datetime))
        # to_dict_op = getattr(item, "to_dict", None)
        # print(to_dict_op)
        # if callable(to_dict_op):
        #     return item.to_dict()

        if isinstance(item, MyJsonConvertable):
            return item.to_dict()

        # elif isinstance(item, list):
        #     if isinstance(item, MyJsonConvertable):
        #         return item.to_dict()

        elif isinstance(item, datetime):
            item: datetime
            # return item.strftime(Config.DEFAULT_DATETIME_FORMAT)
            return str(item)

        else:
            return str(item)
            # return json.dumps(o)


class MyJsonConvertable():
    def to_dict(self, include_class_defaults: bool = True) -> dict:
        """
        Turn the instance into a dict

        Adds all 'public' variables of the instance and the parent class to a dict

        Variables can be excluded by naming them in a '_exclude_vars_' variable.
        '_exclude_vars_' can be a string or a list of strings 
        containing the names of the variables to exclude.

        variables are considered private/not public if they start with '_' or '__'

        Returns
        -------
        dict
            dictionary containg all variables

        Examples
        --------

        With the following class:
        ```
        class Temp():
            _exclude_vars_ = "id" # or ["id"]
            _private_var = "private"
            id = 3
            name = "temp"
            datetime = datetime("01.01.2000") # simplified for demonstration
        ```
        running `Temp.to_dict()` results in the dict:
        ```
        {
            "name": "temp",
            datetime: datetime("01.01.2000") # remains as datetime object
        }
        ```
        """

        def _build_dict(input_dict, input_vars: dict[str], exclude_vars: list[str] | str | None):
            for var_name in input_vars:
                if exclude_vars is None or var_name not in exclude_vars:
                    is_public = not var_name.startswith(("__", "_"))
                    is_funciton = callable(input_vars[var_name])
                    is_class_function = isinstance(
                        input_vars[var_name], classmethod)

                    if is_public and not is_funciton and not is_class_function:

                        if not isinstance(input_vars[var_name], hybrid_property):
                            # print("True")
                            # input_dict[var_name] = input_vars[var_name]()
                            input_dict[var_name] = input_vars[var_name]

            return input_dict

        var_dict = {}
        if include_class_defaults:
            var_dict = _build_dict(var_dict, vars(
                self.__class__), getattr(self.__class__, "_exclude_vars_", None))

        var_dict = _build_dict(var_dict, vars(
            self), getattr(self.__class__, "_exclude_vars_", None))

        return var_dict

    def to_json(self):
        return json.loads(json.dumps(self, cls=MyJsonEncoder))
