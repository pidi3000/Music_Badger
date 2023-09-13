
from flask import Flask, Blueprint

from werkzeug.exceptions import HTTPException
from badger.error import handle_server_exception

blueprint = Blueprint('api', __name__, url_prefix="/api")


def init(app: Flask | Blueprint):
    print("init api")
    # app.debug
    blueprint.register_error_handler(HTTPException, handle_server_exception)

    from . import v1 as api_routes
    api_routes.init(blueprint)

    # from . import v2 as api_routes
    # api_routes.init(blueprint)

    app.register_blueprint(blueprint)
