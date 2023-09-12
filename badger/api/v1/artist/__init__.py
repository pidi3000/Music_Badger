
from flask import Flask, Blueprint

# blueprint = Blueprint('artist', __name__, url_prefix="/artist")
blueprint = Blueprint('artist', __name__)

from . import routes

def init(app: Flask | Blueprint):
    print("init api artist")
    app.register_blueprint(blueprint)
