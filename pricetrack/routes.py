# from aiohttp import web
from resources.users import Hello, UserSignUp, UserLogIn


def setup_routes(app):
    # Hello resource
    app.router.add_view("/", Hello)
    app.router.add_view("/users", UserSignUp)
    app.router.add_view("/users/login", UserLogIn)
