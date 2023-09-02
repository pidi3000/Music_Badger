from . import db
from . import _Base_Mixin

from sqlalchemy.ext.hybrid import hybrid_property


class Audio_File(_Base_Mixin, db.Model):
    __tablename__ = 'audio_file'

    id = db.Column(db.Integer, primary_key=True)

    location = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(200), nullable=False)
    
    audio_length = db.Column(db.Integer)

    def __repr__(self):
        return f'<{self.__class__} {self.name}>'

    @classmethod
    def create(cls, location, name, extension, audio_length) -> 'Audio_File':
        return super().create(location, name, extension, audio_length)


class Image_File(_Base_Mixin, db.Model):
    __tablename__ = 'image_file'

    id = db.Column(db.Integer, primary_key=True)

    location = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<{self.__class__} {self.name}>'

    @classmethod
    def create(cls, location, name, extension) -> 'Image_File':
        return super().create(location, name, extension)
