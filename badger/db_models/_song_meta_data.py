from __future__ import annotations

from badger.extension import db
from badger.db_models import _Base_Mixin
from badger.db_models._files import Audio_File, Image_File
from badger.db_models._song_user_data import Song_User_Data
from badger.db_models._publisher import Publisher
from badger.data_handler.youtube_data_handler import YouTube_Data_Handler

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped

from datetime import datetime
import json

_DEBUG = False


class Song_Meta_Data(_Base_Mixin, db.Model):
    __tablename__ = 'song_meta_data'
    _exclude_vars_ = ["user_data_list"]

    id = db.Column(db.Integer, primary_key=True)

    user_data_list: Mapped[list[Song_User_Data]] = db.relationship(
        'Song_User_Data', back_populates='meta_data')

    ################################
    # Publisher
    ################################
    id_publisher = db.Column(
        db.Integer, db.ForeignKey('publisher.id'), nullable=True)

    publisher: Mapped[Publisher] = db.relationship(
        'Publisher', back_populates='meta_data_list')
    # 'Song_User_Data', backref='meta_data_list')
    # meta_data_id = db.Column(db.Integer, db.ForeignKey('song_meta_data.id'))
    # meta_data = db.relationship('Song_Meta_Data', back_populates='user_data_list')

    ################################
    # YT data
    ################################
    yt_title = db.Column(db.String(200), nullable=True)
    yt_description = db.Column(db.String(200), nullable=True)
    yt_id = db.Column(db.String(200), nullable=False)

    yt_data_raw = db.Column(db.String(10_000), nullable=True)

    ################################
    # Files
    ################################
    ################
    # Audio
    ################
    file_id_audio = db.Column(
        db.Integer, db.ForeignKey('audio_file.id'), nullable=True, unique=True)

    file_audio: Mapped[Audio_File] = db.relationship(
        "Audio_File", uselist=False, backref="meta_data")

    ################
    # Image
    ################
    file_id_image = db.Column(
        db.Integer, db.ForeignKey('image_file.id'), nullable=True, unique=True)

    file_image: Mapped[Image_File] = db.relationship(
        "Image_File", uselist=False, backref="meta_data")

    ################################
    # Dates
    ################################
    date_upload = db.Column(db.DateTime, default=func.now(), nullable=True)
    date_added = db.Column(db.DateTime, default=func.now())
    # date_added = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f'<Song_Meta_Data {self.id}>'

    ################################################################
    # Class functions
    ################################################################
    # https://stackoverflow.com/questions/35814211/how-to-add-a-custom-function-method-in-sqlalchemy-model-to-do-crud-operations

    @classmethod
    def create(cls, yt_id: str) -> Song_Meta_Data:
        """Adds song meta data to collection

        Automatically retrieves YouTube data
        and creates the Publisher if needed

        Parameters
        ----------            
        yt_id : str 
            YouTube ID of the song.

        Returns
        -------
        Song
            Song_Meta_Data instance

        Raises
        ------
        ValueError
            If the yt_id is invalid.

        LookupError
            If a Song with the same yt_id already exists.

        """

        if _DEBUG:
            print("Add song with yt_id: ", yt_id)

        if not yt_id:
            raise ValueError(f"yt_ID invalid: {yt_id}")

        if cls.check_exists(yt_id):
            raise LookupError(f"Song with the yt_ID '{yt_id}' already exists")

        yt_data_handler = YouTube_Data_Handler(yt_id=yt_id)

        yt_data_raw = json.dumps(
            yt_data_handler.yt_data_raw,
            ensure_ascii=False,
            indent=2
        )

        yt_title = yt_data_handler.get_video_title()
        yt_description = yt_data_handler.get_video_description()
        date_upload = yt_data_handler.get_video_published_date()
        channel_id = yt_data_handler.get_channel_Id()
        channel_name = yt_data_handler.get_channel_Title()

        publisher = Publisher.get_by_ytID_or_create(
            yt_id=channel_id, name=channel_name)

        return super().create(
            yt_id=yt_id,
            yt_title=yt_title,
            yt_description=yt_description,
            yt_data_raw=yt_data_raw,
            date_upload=date_upload,
            id_publisher=publisher.id
        )

    @classmethod
    def get(cls, id: int = None, yt_id: str = None) -> Song_Meta_Data | None:
        """Get song from DB by internal ID"""
        if id is None and yt_id is None:
            raise TypeError("at least one parameter mus be set")

        if id is not None:
            return cls.get_by_ID(id)

        return cls.get_by_ytID(yt_id)

    @classmethod
    def get_by_ytID(cls, yt_id: str) -> Song_Meta_Data | None:
        """Get song from DB by YouTube ID"""
        if _DEBUG:
            print("Get song with yt_id: ", yt_id)

        return cls.query.filter_by(yt_id=yt_id).first()

    @classmethod
    def get_or_create(cls, yt_id: str) -> Song_Meta_Data:
        """Get song from DB or create with yt_id"""
        meta_data = Song_Meta_Data.get_by_ytID(yt_id)

        if meta_data is None:
            meta_data = Song_Meta_Data.create(yt_id)

        return meta_data

    @classmethod
    def check_exists(cls, yt_id: str) -> bool:
        """Checks if song already in collection"""
        if _DEBUG:
            print("Check song with yt_id: ", yt_id)

        return cls.get_by_ytID(yt_id) is not None

    ################################################################
    # Instance functions
    ################################################################

    # TODO USER implement this
    def get_user_data(self, user_id=None) -> None | Song_User_Data:
        # get user data based on user id
        if user_id:
            raise NotImplementedError("soon^TM")

        if self.user_data_list and len(self.user_data_list) > 0:
            return self.user_data_list[0]

        return None
