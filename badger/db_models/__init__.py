from __future__ import annotations

from ..extension import db
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import model

import json
from ..extension import MyJsonConvertable


class _Base_Mixin(MyJsonConvertable):

    @classmethod
    def create(cls, **kw) -> _Base_Mixin:
        """Create new entry in DB of this type, no duplicate checks done"""
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

        return obj

    @classmethod
    def get_all(cls) -> list[_Base_Mixin | None]:
        """Get all entrys from DB"""
        return cls.query.all()

    @classmethod
    def get_first(cls) -> _Base_Mixin | None:
        """Get first entry from DB"""
        return cls.query.first()

    @classmethod
    def get_by_ID(cls, id: int) -> _Base_Mixin | None:
        """Get entry by internal ID from DB"""
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_num(cls) -> int:
        """Get number of entrys of this type DB"""
        return len(cls.get_all())

    def delete(self) -> None:
        """Removes object from DB"""
        db.session.delete(self)
        db.session.commit()

    # def to_dict(self, include_class_defaults: bool = True) -> dict:
    #     # print(self.__class__)
    #     var_dict = {}

    #     def _build_dict(input_dict, input_vars: dict[str]):
    #         for var_name in input_vars:
    #             is_public = not var_name.startswith(("__", "_"))
    #             is_funciton = callable(input_vars[var_name])
    #             is_class_function = isinstance(input_vars[var_name], classmethod)
    #             if is_public and not is_funciton and not is_class_function:
    #                 input_dict[var_name] = input_vars[var_name]

    #         return input_dict

    #     class_vars = vars(self.__class__)
    #     instance_vars = vars(self)

    #     if include_class_defaults:
    #         var_dict = _build_dict(var_dict, class_vars)

    #     var_dict = _build_dict(var_dict, instance_vars)

    #     return var_dict

    # def to_json(self):
    #     return json.loads(json.dumps(self, cls=MyJsonEncoder))


# def _import_models():
from ._files import Audio_File
from ._files import Image_File
from ._artist import Artist
from ._publisher import Publisher
from ._song_user_data import Song_User_Data
from ._song_meta_data import Song_Meta_Data


# _import_models()


# Tutorials
# https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy#step-2-setting-up-database-models-for-a-many-to-many-relationship
# https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
