
from flask import Flask, Blueprint

API_VERSION = 1

blueprint = Blueprint(f'v{API_VERSION}', __name__, url_prefix=f"/v{API_VERSION}")

def init(app: Flask | Blueprint):
    print(f"init v{API_VERSION}")

    from . import song as api_routes
    api_routes.init(blueprint)

    from . import artist as api_routes
    api_routes.init(blueprint)

    app.register_blueprint(blueprint)
