
from flask import Flask, Blueprint

blueprint = Blueprint('artist', __name__, url_prefix="/artist")

from . import routes

def init(app: Flask | Blueprint):
    print("init api artist")
    app.register_blueprint(blueprint)
