

from badger.db_models import Song_Meta_Data, Song_User_Data, Artist, Publisher
from badger.extension import MyJsonConvertable

from badger.data_handler.api_response_handler import API_Response_Handler
from badger.data_handler.user_input_handler import User_Input_Handler
from badger.data_handler.youtube_data_handler import YouTube_Data_Handler

from badger.error import BadgerEntryAlreadyExists

_debug = True


class Song(MyJsonConvertable):
    id = None
    # user_id: int = 0

    meta_data: Song_Meta_Data = None
    user_data: Song_User_Data = None

    @classmethod
    def create(cls,
               yt_id: str,
               artist_data: int | str | Artist | list[str | Artist],
               song_title: str | None,
               song_extras: str | list[str] | None
               ):
        # https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard

        # data is auto committed to DB
        # this can lead to stray data in DB if errors occure
        # primarly Song_Meta_Data, Publisher and maybe Artist
        # two possible solutions:
        # 1. only commit on succes, revert/rollback DB on error https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
        # 2. run garbage collection of unused entry
        """
        Adds a new song to the collection

        Parameters
        ----------            
        yt_id : str 
            YouTube ID of the song

        artist_data : Artist, int, str or list
            artist ID,\n
            artist NAME (creats new Artist with name if none exists),\n
            artist CLASS instance,\n
            list of artist NAME (creats new Artist with name if none exists),\n
            list of artist CLASS instance.

        song_title : str 
            Title of the song

        extras : str 
            Extra information about the song (bass boost, nightcore, remix, etc.)

        Returns
        -------
        Song
            The newly created song

        Raises
        ------
        ValueError
            If the yt_id is invalid

        BadgerEntryAlreadyExists
            If a Song with the yt_id already exists\n

        LookupError
            If an Artist with the given id does not exist

        TypeError
            If artist_data is a unsupported data type

        """

        if _debug:
            print()
            print("Adding song with yt_id: ", yt_id)
            print()

        if not yt_id:
            raise ValueError(f"yt_ID invalid: '{yt_id}'")

        if Song.check_exists(yt_id):
            raise BadgerEntryAlreadyExists(
                message=f"Song with the yt_ID '{yt_id}' already exists")

        artist_list = User_Input_Handler.get_artists(artist_data)
        print("DEBUG get:", artist_list)

        song_meta_data = Song_Meta_Data.get_or_create(yt_id)

        user_data = Song_User_Data.create(
            meta_data_id=song_meta_data.id,
            user_artist_data=artist_list,
            user_song_title=song_title,
            user_extras=song_extras
        )

        return Song.get(id=user_data.id)

    ################################################################################################################################
    # Edit
    ################################################################################################################################

    @classmethod
    def edit(cls,
             yt_id: str,
             artist_data: int | str | Artist | list[str | Artist] = None,
             song_title: str | None = None,
             song_extras: str | list[str] | None = None
             ):
        # https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard
        """
        Edit an existing song

        Only the provide attributes are changed

        Parameters
        ----------            
        yt_id : str 
            YouTube ID of the song

        artist_data : Artist, int, str or list
            artist ID,\n
            artist NAME (creats new Artist with name if none exists),\n
            artist CLASS instance,\n
            list of artist NAME (creats new Artist with name if none exists),\n
            list of artist CLASS instance.

        song_title : str 
            Title of the song.

        extras : str 
            Extra information about the song (bass boost, nightcore, remix, etc.)

        Returns
        -------
        Song
            The edited song

        Raises
        ------
        ValueError
            If the yt_id is invalid

        LookupError
            If a Song with the yt_id does not exist\n
            If an Artist with the given id does not exist

        TypeError
            If artist_data is a unsupported data type

        """

        if _debug:
            print()
            print("Editing song with yt_id: ", yt_id)
            print()

        if not yt_id:
            raise ValueError(f"yt_ID invalid: '{yt_id}'")

        if not Song.check_exists(yt_id):
            raise LookupError(f"Song with the yt_ID '{yt_id}' does not exist")

        artist_list = User_Input_Handler.get_artists(artist_data)
        print("DEBUG EDIT get:", artist_list)

        song_meta_data = Song_Meta_Data.get_by_ytID(yt_id)

        user_data = song_meta_data.get_user_data()

        user_data.edit(
            user_artist_list=artist_list,
            user_song_title=song_title,
            user_extras=song_extras
        )

        return Song.get(id=user_data.id)

    ################################################################################################################################
    # Getter
    ################################################################################################################################

    @classmethod
    def get(cls, id: int = None, yt_id: str = None) -> "Song":
        """
        Get Song from DB by internal user_data ID or YouTube ID (prioritizes internal ID)

        Parameters
        ----------
        id : int or str
            The ID used by the Database, MUST be a integer, if it's a string gets converted

        yt_id : str 
            YouTube ID of the song.

        Returns
        -------
        Song
            The newly created song.

        Raises
        ------
        TypeError
            If the id is invalid.
            If the yt_id is invalid.

        LookupError
            If a Song with set prioritized ID does not exist

        """

        # if id is None and yt_id is None:
        #     raise TypeError("at least one parameter must be set")

        user_data = Song_User_Data.get(id=id, yt_id=yt_id)

        # User has not added this song
        ##############################
        # if not Song_User_Data.check_exists(id=id, yt_id=yt_id):
        if user_data is None:
            if id is not None:
                raise LookupError(
                    f"1- Song with the id '{id}' does not exists")
            if yt_id is not None:
                raise LookupError(
                    f"Song with the yt_ID '{yt_id}' does not exists")

            return Exception("uknown error occured")

        user_data: Song_User_Data

        meta_data = user_data.meta_data
        meta_data: Song_Meta_Data

        # print()
        # print()
        # print(user_data.to_dict())
        # print(user_data.to_json())
        # print()
        # print(user_data.artist_list)
        # print()
        # for artist in user_data.artist_list:
        #     print(artist)
        # print()
        # print()
        # pprint(meta_data.to_dict())
        # print()
        # print(meta_data.publisher)
        # print(meta_data.file_audio)
        # print(meta_data.file_image)
        # print()
        # print()

        song = Song()
        song.id = meta_data.id
        song.meta_data = meta_data
        song.user_data = user_data

        return song

    @classmethod
    def get_all(cls):
        """Get all songs from DB"""

        all_user_songs: list[Song_User_Data] = Song_User_Data.get_all()

        all_songs: list[Song] = []

        for user_song_data in all_user_songs:
            all_songs.append(Song.get(id=user_song_data.id))

        return all_songs

    @classmethod
    def get_page(cls, page_num: int = 1, per_page: int = None) -> (list['Song'], API_Response_Handler.API_page_info):
        """Get paged songs from DB"""

        all_user_songs: list[Song_User_Data] = Song_User_Data.get_page(
            page_num=page_num, per_page=per_page)

        all_songs: list[Song] = []

        for user_song_data in all_user_songs:
            all_songs.append(Song.get(id=user_song_data.id))

        page_info = API_Response_Handler.create_page_info(all_user_songs)

        return (all_songs, page_info)

    @classmethod
    def get_info(cls, yt_id: str) -> dict:
        """
        Get Song info extracted from YouTube data

        Creates Song_Meta_Data entry for yt_id and returns dict of autogenerated song data

        Parameters
        ----------
        yt_id : str 
            YouTube ID of the song.

        Returns
        -------
        dict
            Song info extracted from YouTube

        Raises
        ------
        TypeError
            If the yt_id is invalid.

        """

        if not yt_id:
            raise TypeError(f"yt_ID invalid: '{yt_id}'")

        song_meta_data = Song_Meta_Data.get_or_create(yt_id)
        youtube_data_handler = YouTube_Data_Handler(yt_id=yt_id)

        artists = []

        for artist_name in youtube_data_handler.get_song_artist_names():
            artists.append(
                {
                    "id": None,
                    "name": artist_name
                }
            )

        song_dict = {
            "id": None,
            "yt_id": song_meta_data.yt_id,
            "title": youtube_data_handler.get_song_title(),
            "extras": youtube_data_handler.get_song_extras(),
            "artists": artists,
            "publisher": {
                "id": song_meta_data.publisher.id if song_meta_data.publisher else None,
                "name": song_meta_data.publisher.name if song_meta_data.publisher else None
            }
        }

        return song_dict

    ################################################################################################################################
    #
    ################################################################################################################################
    @classmethod
    def check_exists(cls, yt_id: str) -> bool:
        """
        Checks if song already in Song_User_Data
        """
        # if _debug:
        #     print("Check song with yt_id: ", yt_id)

        # return Song_Meta_Data.check_exists(yt_id=yt_id)
        return Song_User_Data.check_exists(yt_id=yt_id)

    def to_dict(self, include_class_defaults: bool = True) -> dict:
        """
        Turns the song into a dict for web transfer

        Returns
        -------
        dict
            dictionary containg relevant information of the song

        Examples
        --------

        The returned dict will have the following structure:
        ```
        {
            "id": 0,
            "yt_id": "",
            "date_added": "",
            "title": "",
            "extras": "",
            "artists": [ # list of all artists
                {
                    "id": 0,
                    "name": "name"
                }
            ],
            "publisher": {
                "id": 0,
                "name": "name"
            }
        }
        ```
        """

        # return super().to_dict()

        artists = []

        i = 0
        for artist in self.user_data.artist_list:
            if i == 0:
                artists.append(
                    {
                        "id": artist.id,
                        "name": artist.name
                    }
                )
                i = 0
            else:  # intentional error for unitest verification
                artists.append(
                    {
                        "id": artist.id,
                        "name": artist.name + "_"
                    }
                )

        song_dict = {
            "id": self.user_data.id,
            "yt_id": self.meta_data.yt_id,
            "date_added": self.user_data.date_added,

            "title": self.user_data.title,
            "extras": self.user_data.extras,
            "artists": artists,
            "publisher": {
                "id": self.meta_data.publisher.id if self.meta_data.publisher else None,
                "name": self.meta_data.publisher.name if self.meta_data.publisher else None
            }
        }

        # TODO FILES add thumbnail and audio path data

        return song_dict
