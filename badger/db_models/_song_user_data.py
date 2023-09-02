from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ._artist import Artist
    from ._song_meta_data import Song_Meta_Data

from . import db
from . import _Base_Mixin
# from ._artist import Artist
from ._artist_song import _artist_song
from ..data_handler.youtube_data_handler import YouTube_Data_Handler

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped


class Song_User_Data(_Base_Mixin, db.Model):
    __tablename__ = 'song_user_data'
    _exclude_vars_ = ["meta_data"]

    id: int = db.Column(db.Integer, primary_key=True)

    artist_list: Mapped[list[Artist]] = db.relationship(
        'Artist', secondary=_artist_song, back_populates='song_user_data_list')

    ################################
    # Meta Data
    ################################
    meta_data_id = db.Column(db.Integer, db.ForeignKey('song_meta_data.id'))

    meta_data: Mapped[Song_Meta_Data] = db.relationship(
        'Song_Meta_Data', back_populates='user_data_list')

    ################################
    # info
    ################################
    name: str = db.Column(db.String(200), nullable=False)
    extras: str = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f'<Song_User_Data {self.name}>'

    ################################################################
    # Class functions
    ################################################################

    # https://stackoverflow.com/questions/35814211/how-to-add-a-custom-function-method-in-sqlalchemy-model-to-do-crud-operations

    @classmethod
    def create(cls,
               meta_data_id: int,
               user_artist_data: Artist | list[Artist] | None = None,
               user_song_title: str | None = None,
               user_extras: str | list[str] | None = None
               ) -> Song_User_Data:

        from ._song_meta_data import Song_Meta_Data
        yt_data_handler = YouTube_Data_Handler(
            yt_id=Song_Meta_Data.get(id=meta_data_id).yt_id)

        user_data: Song_User_Data = super().create(
            name=yt_data_handler.get_song_title(user_song_title),
            extras=yt_data_handler.get_song_extras(user_extras),
            meta_data_id=meta_data_id
        )

        print("DEBUG create:", user_artist_data)
        artist_list = yt_data_handler.get_song_artists(user_artist_data)
        print("DEBUG create:", artist_list)
        user_data.artist_list.extend(artist_list)
        db.session.commit()

        return user_data

    ################################################################
    # Getter Class functions
    ################################################################

    @classmethod
    def get(cls, id: int = None, yt_id: str = None) -> Song_User_Data | None:
        """
        Get Song_User_Data from DB by internal user_data ID or YouTube ID (prioritizes internal ID)

        Parameters
        ----------
        id : int
            The ID used by the Database, MUST be a `int`

        yt_id : str 
            YouTube ID of the song.

        Returns
        -------
        Song_User_Data
            The Song_User_Data from DB

        None
            If no Song_User_Data for the prioritized ID exists

        Raises
        ------
        TypeError
            If id and yt_id is `None`.\n
            if id is set and not a `int`.\n
            if yt_id set and not a `str`.\n

        ValueError
            If yt_id set and is an empty string.
        """

        # check one var is set
        if id is None and yt_id is None:
            raise TypeError(
                f"One of id or yt_id parameter must be set, got id: '{id}' yt_id: '{yt_id}'.")

        # if id is valid value and type
        if id is not None:
            if not isinstance(id, int):
                raise TypeError(f"id is not of type `int`: '{type(id)}'")

            return cls.get_by_ID(id=id)

        # else if yt_id is valid

        if not isinstance(yt_id, str):
            raise TypeError(f"yt_id is not of type `str`: '{type(yt_id)}'")

        if len(yt_id) < 1 or yt_id.isspace():
            raise ValueError(f"yt_id is a empty string: {yt_id}")

        return cls.get_by_ytID(yt_id=yt_id)

    @classmethod
    def get_by_meta_data_ID(cls, meta_data_id: int) -> Song_Meta_Data | None:
        """Get user_data from DB by meta_data ID"""

        from ._song_meta_data import Song_Meta_Data
        meata_data: Song_Meta_Data = Song_Meta_Data.get_by_ID(id=meta_data_id)

        return meata_data.get_user_data() if meata_data is not None else None
        # return meata_data.user_data_list[0] if meata_data is not None and len(meata_data.user_data_list) > 0 else None

    @classmethod
    def get_by_ytID(cls, yt_id: str) -> Song_User_Data | None:
        """Get user_data from DB by YouTube ID"""

        from ._song_meta_data import Song_Meta_Data
        meata_data: Song_Meta_Data = Song_Meta_Data.get_by_ytID(yt_id=yt_id)

        return meata_data.get_user_data() if meata_data is not None else None
        # return meata_data.user_data_list[0] if meata_data is not None and len(meata_data.user_data_list) > 0 else None
        # return cls.query.filter_by(yt_id=yt_id).first()

    ################################################################
    #
    ################################################################
    @classmethod
    def check_exists(cls, id: int = None, yt_id: str = None) -> bool:
        """Checks if song already in collection"""

        # Ensure one id is set
        if id is None and yt_id is None:
            raise TypeError("Either id or yt_id parameter must be set.")

        # return True
        # from ._song_meta_data import Song_Meta_Data
        # return Song_Meta_Data.get_by_ytID(yt_id=yt_id) is not None

        return Song_User_Data.get(id=id, yt_id=yt_id) is not None

        return cls.get_by_ytID(yt_id) is not None

    ################################################################
    # Instance functions
    ################################################################

    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html

    def edit(self,
             user_artist_list: Artist | list[Artist] | None = None,
             user_song_title: str | None = None,
             user_extras: str | list[str] | None = None
             ) -> Song_User_Data:

        self.name = user_song_title
        self.extras = user_extras

        self.artist_list.clear()
        self.artist_list.extend(user_artist_list)
        # print("DEBUG create:", artist_list)

        db.session.commit()

        # return user_data

    # @hybrid_property
    # def yt_link(self) -> str:
    #     return "https://www.youtube.com/channel/" + self.yt_id
