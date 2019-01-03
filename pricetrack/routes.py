# from aiohttp import web
from resources.users import Hello, UserSignUp, UserLogIn, UserThatIsMe, UserLogInWithGoogle
from resources.items import ItemsResource, OneItemResource


def setup_routes(app):
    # Hello resource
    app.router.add_view("/", Hello)
    app.router.add_view("/users", UserSignUp)
    app.router.add_view("/users/login", UserLogIn)
    app.router.add_view("/users/login/google", UserLogInWithGoogle)
    app.router.add_view("/users/me", UserThatIsMe)
    app.router.add_view("/items", ItemsResource)
    app.router.add_view("/items/{item_id}", OneItemResource)
