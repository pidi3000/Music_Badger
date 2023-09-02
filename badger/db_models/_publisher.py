from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # from ._artist import Artist
    from ._song_meta_data import Song_Meta_Data

from . import db
from . import _Base_Mixin

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped


class Publisher(_Base_Mixin, db.Model):
    __tablename__ = 'publisher'

    id: int = db.Column(db.Integer, primary_key=True)
    yt_id: str = db.Column(db.String(200), nullable=False)

    name: str = db.Column(db.String(200), nullable=False)

    # meta_data_id = db.Column(db.Integer, db.ForeignKey('song_meta_data.id'))
    meta_data_list: Mapped[list[Song_Meta_Data]] = db.relationship(
        'Song_Meta_Data', back_populates='publisher')

    def __repr__(self):
        return f'<{self.__class__} {self.name}>'

    ################################################################
    # Class functions
    ################################################################

    # https://stackoverflow.com/questions/35814211/how-to-add-a-custom-function-method-in-sqlalchemy-model-to-do-crud-operations

    @classmethod
    def create(cls, yt_id:str, name:str) -> Publisher:
        name = name.strip()
        return super().create(yt_id=yt_id, name=name)

    
    @classmethod
    def get_by_ytID_or_create(cls, yt_id:str, name:str) -> Publisher:
        publisher = Publisher.get_by_ytID(yt_id)

        if publisher is None:
            publisher = Publisher.create(yt_id, name)

        return publisher

    @classmethod
    def get_by_ytID(cls, yt_id:str) -> Publisher | None:
        return Publisher.query.filter_by(yt_id=yt_id).first()

    ################################################################
    # Instance functions
    ################################################################

    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html

    # @hybrid_property
    # def yt_link(self) -> str:
    #     return "https://www.youtube.com/channel/" + self.yt_id
