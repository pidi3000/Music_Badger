
from flask import Flask, Blueprint

blueprint = Blueprint('api', __name__, url_prefix="/api")


def init(app: Flask | Blueprint):
    print("init api")

    from . import v1 as api_routes
    api_routes.init(blueprint)

    # from . import v2 as api_routes
    # api_routes.init(blueprint)

    app.register_blueprint(blueprint)
