from aiohttp import web
from routes import setup_routes
import logging


def create_app():
    app = web.Application()
    setup_routes(app)
    return app

if __name__ == "__main__":
    app = create_app()
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app)
