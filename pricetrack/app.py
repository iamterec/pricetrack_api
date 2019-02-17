from aiohttp import web
from authorization import auth_middleware
from routes import setup_routes
import logging
from extensions import apply_cors


def create_app():
    app = web.Application(middlewares=[auth_middleware])
    setup_routes(app)
    apply_cors(app)
    return app

if __name__ == "__main__":
    app = create_app()
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app)
