
from flask import Flask, Blueprint

# blueprint = Blueprint('song', __name__, url_prefix="/song")
blueprint = Blueprint('song', __name__)

from . import routes

def init(app: Flask | Blueprint):
    print("init api song")
    app.register_blueprint(blueprint)
