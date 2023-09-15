
from flask import Flask, Blueprint

blueprint = Blueprint('yt_auth', __name__)

from . import routes

def init(app: Flask | Blueprint):
    print("init api yt_auth")
    app.register_blueprint(blueprint)
