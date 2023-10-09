from __future__ import annotations

from flask_sqlalchemy.pagination import Pagination
from flask_sqlalchemy import SQLAlchemy, model

from badger.extension import db
from badger.extension import MyJsonConvertable

from badger.config import app_config


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
    def get_page(cls, page_num: int = 1, per_page: int = None) -> Pagination:
        # 
        # docs fucntion parameters: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/api/#flask_sqlalchemy.SQLAlchemy.paginate
        # docs page properties: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/api/#flask_sqlalchemy.pagination.Pagination
        # docs how to: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/pagination/
        # https://www.digitalocean.com/community/tutorials/how-to-query-tables-and-paginate-data-in-flask-sqlalchemy#step-4-ordering-limiting-and-counting-results
        """Get page entrys from DB

        Parameters
        ----------
        page_num
            the page number to get
        
        per_page
            Default: set in config using ENTRYS_PER_PAGE
            Number of entrys per page.

        """
        
        if per_page is None:
            per_page = app_config.badger.ENTRYS_PER_PAGE
            
        print(page_num)

        return cls.query.paginate(
            page=page_num,
            per_page=per_page,
            error_out=False
        )

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
from ._song_meta_data import Song_Meta_Data
from ._song_user_data import Song_User_Data
from ._publisher import Publisher
from ._artist import Artist
from ._files import Image_File
from ._files import Audio_File

# _import_models()


# Tutorials
# https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy#step-2-setting-up-database-models-for-a-many-to-many-relationship
# https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
