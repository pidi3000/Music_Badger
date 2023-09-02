# from __future__ import annotations

from re import match
from datetime import datetime
import json

from .extension import MyJsonEncoder


# TODO move this to User_Input_Handler class
def exception_to_dict(exception: Exception):
    return {
        "error": {
            "type": str(exception.__class__.__name__),
            "msg": str(exception)}
    }


def obj_list_to_json(list) -> dict:
    """Turn a list of custom classes into json serializable dict"""
    return json.loads(json.dumps(list, cls=MyJsonEncoder))


def extract_yt_ID(yt_link: str) -> str | None:
    if yt_link is None:
        return None

    if "youtu.be" in yt_link:  # link looks like "https://youtu.be/ABCDEFG" can NOT have trailing "/"
        print("extracting id from link: ", yt_link)
        return yt_link.removesuffix("/").split("/")[-1]

    elif "youtube.com" in yt_link:  # link looks like "https://www.youtube.com/watch?v=ABCDEFG&list=asdfgh&index=10"
        print("extracting id from link: ", yt_link)
        return yt_link.split("v=")[-1].split("&")[0]

    else:
        raise ValueError(f"yt link invalid: '{yt_link}'")


def get_as_type_or_none(value: int | float | str | list, return_type: int | float | str, allow_epmty_str: bool = False, is_list: bool = False):
    """
    Attempts to convert `value` to the type set by `return_type`

    Parameters
    ----------
    value : int or str
        The data to convert

    return_type : str 
        The desired data type

    allow_epmty_str : bool
        If `value` results in a empty or white space only string and `allow_epmty_str == False`, `None` is returned 

    is_list: bool
        if `value` is a list,


    Returns
    -------
    type[return_type]
        `Value` with the type set by `return_type` if convertable

    list[type[return_type]]
        list with the enrtys of `value` in the set type or None 

    None
        If `Value` can't be converted,\n
        `Value` is of type `None`.\n
    """

    # print("DEBUG convert{: ")
    # print(value)
    # print(type(value))
    # print(isinstance(value, list))
    # print("}\n")

    is_list = isinstance(value, list)

    if is_list:
        value_list = []
        only_None = True

        for val in value:
            data = get_as_type_or_none(
                value=val,
                return_type=return_type,
                allow_epmty_str=allow_epmty_str,
                is_list=False)

            if data is not None:
                only_None = False
            value_list.append(data)

        return value_list if not only_None else None

    else:
        if value is None:
            return None

        if return_type == int:
            return get_int_or_none(value)

        elif return_type == float:
            return get_float_or_none(value)

        elif return_type == str:
            return get_str_or_none(value, allow_epmty_str)

    raise TypeError(f"Unsupported return_type set: {return_type}")


def get_int_or_none(value) -> int | None:
    # return int(number) if number and match(
    #     r'^-?[0-9]+$', number) else None
    try:
        return int(value)
    except ValueError as e:
        return None


def get_float_or_none(value) -> float | None:
    try:
        return float(value)
    except ValueError as e:
        return None


def get_str_or_none(value, allow_epmty_str: bool = False) -> str | None:
    """
    Attempts to convert value to string

    If `value` results in a empty or white space only string and `allow_epmty_str == False`, `None` is returned 
    """
    try:
        return_value = str(value)
        # print(len(return_value))
        if not allow_epmty_str and (len(return_value) == 0 or return_value.isspace()):
            return_value = None

        return return_value
    except ValueError as e:
        return None


def get_time_group(time: datetime) -> str:
    time_groups = {
        "today": "Today",
        "yesterday": "Yesterday",

        "week": "This Week",
        "last_week": "Last Week",

        "month": "This Month",
        "last_month": "Last Month",

        "year": "This Year",
        "last_year": "Last Year",

        "older": "Long Ago",
    }

    time_now = datetime.now()
    time_elapsed = time_now - time

    # Day
    hours_ago = time_elapsed.total_seconds()/60/60
    if hours_ago <= 24:
        return time_groups["today"]

    if hours_ago <= 48:
        return time_groups["yesterday"]

    # Week
    days_ago = time_elapsed.total_seconds()/60/60/24
    if days_ago <= 7:
        return time_groups["week"]

    if days_ago <= 14:
        return time_groups["last_week"]

    # Month
    if days_ago <= 30:
        return time_groups["month"]

    if days_ago <= 60:
        return time_groups["last_month"]

    # Year
    if days_ago <= 365:
        return time_groups["year"]

    # Older
    return time_groups["older"]


def get_relative_time(time: datetime) -> str:
    time_now = datetime.now()

    # test_time = "2023-07-09T03:00:00"
    # time_now = datetime.strptime(test_time, YT_DATE_FORMAT)

    time_elapsed = time_now - time

    # print(time_elapsed)
    # print(time_elapsed.seconds)
    # print(time_elapsed.total_seconds())
    # print(time_elapsed.total_seconds() - (time_elapsed.days*24*60*60))
    # print(time_elapsed.days)

    # n seconds ago < 60
    time_section = time_elapsed.total_seconds()
    if time_section < 60:
        return "{} Seconds ago".format(int(time_section))

    # n Minutes ago < 60
    time_section = time_elapsed.total_seconds()/60
    if time_section < 60:
        return "{} Minutes ago".format(int(time_section))

    # n hours ago < 24
    time_section = time_elapsed.total_seconds()/60/60
    if time_section < 24:
        return "{} Hours ago".format(round(time_section, 1))

    # n days ago < 14
    time_section = time_elapsed.total_seconds()/60/60/24
    if time_section < 14:
        return "{} Days ago".format(round(time_section, 1))

    # n weeks ago < 4
    time_section = time_elapsed.total_seconds()/60/60/24/7
    if time_section < 4:
        return "{} Weeks ago".format(round(time_section, 1))

    # n months ago < 12     1 month = 30 days
    time_section = time_elapsed.total_seconds()/60/60/24/30
    if time_section < 12:
        return "{} Months ago".format(round(time_section, 1))

    # n years ago
    time_section = time_elapsed.total_seconds()/60/60/24/365
    return "{} Years ago".format(round(time_section, 1))
