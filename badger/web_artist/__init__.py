
from flask import Flask, Blueprint

blueprint = Blueprint('artist', __name__, url_prefix="/artist",
                      template_folder='templates_artist')

from . import routes

def init(app: Flask):
    print("init artist")
    app.register_blueprint(blueprint)
