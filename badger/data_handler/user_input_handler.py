from ..db_models import Artist

class User_Input_Handler:

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
