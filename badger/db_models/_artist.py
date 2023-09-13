from __future__ import annotations

from badger.extension import db
from badger.db_models import _Base_Mixin
from badger.db_models._song_user_data import Song_User_Data
from badger.db_models._artist_song import _artist_song

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped


class Artist(_Base_Mixin, db.Model):
    __tablename__ = 'artist'
    _exclude_vars_ = ["song_user_data_list"]

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(200), nullable=False)

    song_user_data_list: Mapped[list[Song_User_Data]] = db.relationship('Song_User_Data', secondary=_artist_song,
                                                                        back_populates='artist_list')

    def __repr__(self):
        return f'<{self.__class__} {self.name}>'

    ################################################################
    # Class functions
    ################################################################

    # https://stackoverflow.com/questions/35814211/how-to-add-a-custom-function-method-in-sqlalchemy-model-to-do-crud-operations

    @classmethod
    def create(cls, name: str) -> Artist:
        name = name.strip()
        return super().create(name=name)

    @classmethod
    def get_or_create(cls, name: str) -> 'Artist':
        artist = Artist.get_by_name(name=name)

        if artist is None:
            artist = Artist.create(name)

        return artist

    @classmethod
    def get_by_name(cls, name: str) -> Artist | None:
        name = name.strip()
        return Artist.query.filter_by(name=name).first()

    ################################################################
    # Instance functions
    ################################################################

    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html

    @hybrid_property
    def num_songs(self) -> int:
        return len(self.song_user_data_list)

    def to_dict(self, include_class_defaults: bool = True) -> dict:
        """
        Turns the Artist into a dict for web transfer

        Returns
        -------
        dict
            dictionary containg relevant information of the Artist

        Examples
        --------

        The returned dict will have the following structure:
        ```
        {
            "id": 0,
            "name": "",
            "num_songs": 0
        }
        ```
        """
        artist_dict = super().to_dict(include_class_defaults)
        artist_dict["num_songs"] = self.num_songs

        return artist_dict
