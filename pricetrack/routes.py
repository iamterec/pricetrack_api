from resources.users import UserSignUp, UserLogIn, UserThatIsMe,\
                            UserLogInWithGoogle, UserPasswordReset, UserPasswordChange
from resources.items import ItemsResource, OneItemResource


def setup_routes(app):
    app.router.add_view("/users", UserSignUp)
    app.router.add_view("/users/login", UserLogIn)
    app.router.add_view("/users/login/google", UserLogInWithGoogle)
    app.router.add_view("/users/password-reset", UserPasswordReset)
    app.router.add_view("/users/password-change", UserPasswordChange)
    app.router.add_view("/users/me", UserThatIsMe)

    app.router.add_view("/items", ItemsResource)
    app.router.add_view("/items/{item_id}", OneItemResource)
