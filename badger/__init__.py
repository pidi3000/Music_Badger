"""
App factory init
"""

import os

from celery import Celery

import flask
from flask import Flask, render_template, Response, url_for, redirect, request
from flask_session import Session
from flask_migrate import Migrate

badger_app:Flask = None

def _register_all_blueprints(app: Flask):

    from badger import api as routes
    routes.init(app)

    from badger import web_song as routes
    routes.init(app)

    from badger import web_artist as routes
    routes.init(app)

    from badger import web_youtube as routes
    routes.init(app)

    pass


def _register_base_routes(app: Flask):
    base_template_dir = os.path.abspath(os.path.dirname(__file__))
    # db_path = os.path.join(base_template_dir, 'database.db')
    # print(base_template_dir)
    # print(os.path.join(base_template_dir, "templates/stylesheets/{}.css".format("stylesheetName")))

    def _get_absolute_path(relative_path):
        # return None
        return os.path.join(base_template_dir, relative_path)

    @app.route('/')
    def index():
        return redirect(url_for('song.index'))

    @app.route('/yt/oauth2callback')
    def adasdasd():
        return request.url

    @app.route("/style/<stylesheetName>.css")
    def returnStyle(stylesheetName):

        print(stylesheetName)

        with open(_get_absolute_path("templates/stylesheets/{}.css".format(stylesheetName)), "r", encoding="utf-8") as file:
            stylesheet = file.read()

        return Response(stylesheet, mimetype="text/css")

    @app.route("/scripts/<scriptName>.js")
    def return_Script(scriptName):

        print(scriptName)

        with open(_get_absolute_path("templates/scripts/{}.js".format(scriptName)), "r", encoding="utf-8") as file:
            stylesheet = file.read()

        return Response(stylesheet, mimetype="application/javascript")

    @app.route('/test/')
    def test_page():
        # from badger.data_handler.youtube_data_handler import get_video_data_raw
        # return get_video_data_raw("LP_qEm1BKiw")
        # flask.session["test_stuff"] = "123456789"
        print(flask.session.get("test_stuff"))
        flask.session.pop("test_stuff")
        print(flask.session.get("test_stuff"))

        return '<h1>Testing the Flask Application Factory Pattern</h1>'


def _init_db(app: Flask):
    from badger.extension import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from badger import db_models
    # with app.app_context():
    #     db.create_all()


def _init_session(app: Flask):
    Session(app)
    # sess = Session()
    # sess.init_app(app)


def _init_config(app: Flask):
    from badger.config import app_config
    app_config.sync()

    app.config.from_object(app_config.flask)


def init_with_app(app: Flask):
    # print(Config.SQLALCHEMY_DATABASE_URI)
    _init_session(app)
    _init_db(app)

    _register_all_blueprints(app)
    _register_base_routes(app)


def celery_init_app(app: Flask) -> Celery:
    from badger.config import app_config

    # class FlaskTask(Celery.Task):
    #     def __call__(self, *args: object, **kwargs: object) -> object:
    #         with app.app_context():
    #             return self.run(*args, **kwargs)

    # celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app = Celery(app.name)
    # celery_app.Task = FlaskTask
    celery_app.config_from_object(dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=False,
    )
    )
    # celery_app.config_from_object(app_config.celery)
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app() -> Flask:
    """
    Create app using settings defined in instace

    Parameters
    ----------

    config
        instace with FLASK settings as variabels
    """
    
    global badger_app

    app = Flask(__name__)
    _init_config(app)
    
    app.app_context().push()

    init_with_app(app)
    celery_init_app(app)
    
    badger_app = app

    return app
