from ..db_models import Artist


class User_Input_Handler:
    # TODO do proper sanitizing to avoid SQL injection and stuff like that
    """
    Clean and sanitize user input
    """

    @classmethod
    def get_artists(cls, artist_data: int | str | Artist | list[str | Artist]) -> list[Artist]:
        """
        Gets artist instances using a variety of user supplyed artist information

        Parameters
        ----------

        artist_data : Artist, int, str or list
            artist ID,\n
            artist NAME (creats new Artist with name if none exists),\n
            artist CLASS instance,\n
            list of artist NAME (creats new Artist with name if none exists),\n
            list of artist CLASS instance.

        Raises
        ------

        LookupError
            If an Artist with the given id does not exist.

        TypeError
            If artist_data is a unsupported data type
        """
        artist_list = []

        if isinstance(artist_data, list):
            print()
            print("DEBUG: Artist data: ", type(artist_data))
            print("DEBUG: Artist data: ", artist_data)

            for artist_entry in artist_data:
                if isinstance(artist_entry, str):
                    artist_names = artist_entry.split(",")

                    for name in artist_names:
                        data = cls._get_artist_from_web_data(name)

                        if data is not None:
                            artist_list.append(data)

                else:
                    data = cls._get_artist_from_web_data(artist_entry)

                    if data is not None:
                        artist_list.append(data)
        else:
            data = cls._get_artist_from_web_data(artist_data)
            if data is not None:
                artist_list.append(data)

        return artist_list

    @classmethod
    def _get_artist_from_web_data(cls, artist_data: int | str | Artist) -> Artist | None:
        """

        Parameters
        ----------

        artist_data : Artist, int, str or list
            artist ID,\n
            artist NAME (creats new Artist with name if none exists),\n
            artist CLASS instance,\n
            list of artist NAME (creats new Artist with name if none exists),\n
            list of artist CLASS instance.

        Raises
        ------

        LookupError
            If an Artist with the given id does not exist.

        TypeError
            If artist_data is a unsupported data type
        """

        print()
        print("DEBUG: Artist data: ", type(artist_data))
        print("DEBUG: Artist data: ", artist_data)

        if artist_data is None:
            return None

        if isinstance(artist_data, int):
            artist = Artist.get_by_ID(artist_data)
            if artist is None:
                raise LookupError(f"Artist ID invalid: '{artist_data}'")
            return artist

        if isinstance(artist_data, str):
            return Artist.get_or_create(artist_data.strip())

        if isinstance(artist_data, Artist):
            return artist_data

        raise TypeError(
            f"artist_data is of unsupported type: {type(artist_data)}")

    @classmethod
    def extract_yt_ID(cls, yt_link: str) -> str | None:
        """
        Extract YouTube video ID from a YouTube link

        Parameters
        ----------
        yt_link : str
            YouTube link in one of the following formats:\n
            1 youtu.be/`yt_id`\n
            2 youtube.com/watch?v=`yt_id`[&index=10] (can have more URL parameters but 'v=' MUST containe the video ID)

        Returns
        -------
        `str`
            contains the YouTube ideo ID

        `None`
            if yt_link is `None`

        Raises
        ------
        ValueError
            if no supported format is found for `yt_link`

        """
        if yt_link is None:
            return None

        if "youtu.be" in yt_link:  # link looks like "https://youtu.be/ABCDEFG" can NOT have trailing "/"
            print("extracting id from link: ", yt_link)
            return yt_link.removesuffix("/").split("/")[-1]

        elif "youtube.com" in yt_link:  # link looks like "https://www.youtube.com/watch?v=ABCDEFG&list=asdfgh&index=10"
            print("extracting id from link: ", yt_link)
            return yt_link.split("v=")[-1].split("&")[0]

        raise ValueError(f"yt link invalid: '{yt_link}'")

    ####################################################################################################
    # Get as type
    ####################################################################################################

    @classmethod
    def get_as_type_or_none(cls, value: int | float | str | list, return_type: int | float | str, allow_epmty_str: bool = False, is_list: bool = False):
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
                data = cls.get_as_type_or_none(
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
                return cls.get_int_or_none(value)

            elif return_type == float:
                return cls.get_float_or_none(value)

            elif return_type == str:
                return cls.get_str_or_none(value, allow_epmty_str)

        raise TypeError(f"Unsupported return_type set: {return_type}")

    @classmethod
    def get_int_or_none(cls, value) -> int | None:
        # return int(number) if number and match(
        #     r'^-?[0-9]+$', number) else None
        try:
            return int(value)
        except ValueError as e:
            return None

    @classmethod
    def get_float_or_none(cls, value) -> float | None:
        try:
            return float(value)
        except ValueError as e:
            return None

    @classmethod
    def get_str_or_none(cls, value, allow_epmty_str: bool = False) -> str | None:
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
