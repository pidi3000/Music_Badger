
from flask import Flask, Blueprint

blueprint = Blueprint('song', __name__, url_prefix="/song",
                      template_folder='templates_song')

from . import routes

def init(app: Flask):
    print("init song")
    app.register_blueprint(blueprint)
