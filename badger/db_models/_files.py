from __future__ import annotations

from badger.extension import db
from badger.db_models import _Base_Mixin

from sqlalchemy.ext.hybrid import hybrid_property


class Download_Queue(_Base_Mixin, db.Model):
    __tablename__ = 'download_queue'

    id = db.Column(db.Integer, db.ForeignKey(
        'song_meta_data.id'), primary_key=True)
    task_id: str = db.Column(db.String(200), nullable=False)

    @classmethod
    def create(cls, song_id: int, task_id: str) -> Download_Queue:
        return super().create(id=song_id, task_id=task_id)

    @classmethod
    def get(cls, song_id: int = None, task_id: str = None) -> Download_Queue | None:

        if isinstance(song_id, int):
            return cls.get_by_ID(song_id)

        if isinstance(task_id, str):
            return cls.get_by_Task_ID(task_id)

        raise ValueError("Either song_id or task_id must be set")

    @classmethod
    def get_by_Task_ID(cls, task_id: str) -> Download_Queue | None:
        return Download_Queue.query.filter_by(task_id=task_id).firts()


class Audio_File(db.Model):
    __tablename__ = 'audio_file'

    id = db.Column(db.Integer, primary_key=True)

    location = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(200), nullable=False)

    dl_status = db.Column(db.String(200), nullable=False, default="pending")

    audio_length = db.Column(db.Integer)

    @classmethod
    def create(cls, location, name, extension, audio_length) -> Audio_File:
        return super().create(location, name, extension, audio_length)


class Image_File(db.Model):
    __tablename__ = 'image_file'

    id = db.Column(db.Integer, primary_key=True)

    location = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(200), nullable=False)

    dl_status = db.Column(db.String(200), nullable=False, default="pending")

    @classmethod
    def create(cls, location, name, extension) -> Image_File:
        return super().create(location, name, extension)
