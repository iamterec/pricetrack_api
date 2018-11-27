from aiohttp import web
from resources.users import Hello


def setup_routes(app):
    # Hello resource
    app.router.add_view("/", Hello)
