import logging
from aiohttp import web
from authorization import auth_middleware
from extensions import apply_cors, setup_database
from routes import setup_routes


def create_app(loop=None):
    app = web.Application(middlewares=[auth_middleware])
    setup_database(app, loop)
    setup_routes(app)
    apply_cors(app)
    return app


if __name__ == "__main__":
    app = create_app()
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app)
