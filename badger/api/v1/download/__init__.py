
from flask import Flask, Blueprint

# blueprint = Blueprint('song', __name__, url_prefix="/song")
blueprint = Blueprint('download', __name__)

from . import routes

def init(app: Flask | Blueprint):
    print("init api download")
    app.register_blueprint(blueprint)
