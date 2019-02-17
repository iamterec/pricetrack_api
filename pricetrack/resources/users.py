from aiohttp import web
from config.secret_settings import SecretConfig, EmailSecret
from json import JSONDecodeError
from aiohttp_cors import CorsViewMixin
from pymongo.errors import DuplicateKeyError, CollectionInvalid
from cerberus import Validator
from models.user import User, UserDoesNotExist
import jwt
from authorization import login_required
import requests
from requests import HTTPError
import random
import string
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired
from tasks.email import send_reset_link


class UserSignUp(web.View, CorsViewMixin):
    def validate_data(self, data):
        schema = {"email": {"required": True, "type": "string", "minlength": 6,
                            "regex": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"},
                  "password": {"required": True, "type": "string", "minlength": 3}}
        validator = Validator(schema)
        result = validator.validate(data)
        if not result:
            return validator.errors, 400

    async def post(self):
        data = await self.request.json()

        # validate data
        validation = self.validate_data(data)
        if validation:  # if validation contains errors
            return web.json_response({"errors": validation[0]}, status=validation[1])

        # create user
        user = User(email=data["email"])
        user.set_password(data["password"])
        try:
            await user.save()
        except DuplicateKeyError:  # if user already exist
            return web.json_response({"errors": {"email": ["User with this email alredy exist"]}}, status=409)
        except CollectionInvalid:  # if mongodb collection's validation fails
            return web.json_response({"errors": {"email": ["Invalid data"]}})

        return web.json_response({"msg": "User has been created"})


class UserThatIsMe(web.View, CorsViewMixin):
    @login_required
    async def get(self):
        return web.json_response({"user": self.request.user.get_dict()})

    @login_required
    async def put(self):
        user = self.request.user
        data = await self.request.json()
        if data.get("avatar", False):
            user.data["avatar"] = data["avatar"]
        if data.get("username", False):
            user.data["username"] = data["username"]

        try:
            await user.save()
        except CollectionInvalid:
            return web.json_response({"error": "Invalid data"})

        return web.json_response({"msg": "Your data has been updated"})


class UserLogIn(web.View, CorsViewMixin):

    async def post(self):
        data = await self.request.json()
        try:
            user = await User.get(email=data["email"])
        except UserDoesNotExist:
            return web.json_response({"errors": ["Wrong credentials"]}, status=400)

        # check password
        if not user.check_password(data["password"]):
            return web.json_response({"errors": ["Wrong credentials"]}, status=400)

        payload = {
            "user_id": str(user.data["_id"])
        }
        access_token = jwt.encode(payload, SecretConfig.JWT_SECRET)
        return web.json_response({"access_token": access_token.decode()})


def generate_random_string(length):
    return "".join(random.choice(string.ascii_uppercase +
                                 string.ascii_lowercase +
                                 string.digits) for _ in range(length))


class UserLogInWithGoogle(web.View, CorsViewMixin):
    async def post(self):
        data = await self.request.json()
        access_token = data.get("access_token", None)
        if not access_token:
            return web.json_response({"msg": "You must pass the token"}, status=400)

        # get information about user
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
        try:
            response = requests.get(url, headers={"Authorization": "Bearer " + access_token})
            response.raise_for_status()
            user_info = response.json()
        except HTTPError:
            return web.json_response({"error": "Can not access google servises, wrong token"}, status=400)
        except JSONDecodeError:
            return web.json_response({"error": "Wrong response from google servises"}, status=500)

        # manage user and generate jwt token
        try:
            user = await User.get(email=user_info["email"])
        except UserDoesNotExist:
            # register new user
            user = User(email=user_info["email"], username=user_info["name"],
                        avatar=user_info["picture"])
            random_str = generate_random_string(14)  # set random password for user
            user.set_password(random_str)
            try:
                user_id = await user.save()
            except CollectionInvalid:
                return web.json_response({"error": "Invalid data was recived from your accaunt"}, status=500)

            jwt_token = jwt.encode({"user_id": str(user_id)}, SecretConfig.JWT_SECRET)
        else:
            # user already registered, create JWT token for him
            jwt_token = jwt.encode({"user_id": str(user.data["_id"])}, SecretConfig.JWT_SECRET)

        return web.json_response({"access_token": jwt_token.decode()})


serializer = URLSafeTimedSerializer(EmailSecret.EMAIL_SECRET_KEY)


class UserPasswordReset(web.View, CorsViewMixin):
    async def post(self):
        data = await self.request.json()
        if not data.get("email", None):
            return web.json_response({"error": "You should provide your e-mail address"}, status=400)

        try:
            await User.get(email=data["email"])
        except UserDoesNotExist:
            return web.json_response({"error": "User doesn't exist."}, status=404)

        token = serializer.dumps(data["email"], salt=EmailSecret.EMAIL_SALT)
        send_reset_link.delay(data["email"], token)  # give task to the Celery
        return web.json_response({"msg": "Check your mails"})


class UserPasswordChange(web.View, CorsViewMixin):
    async def post(self):
        print("Hello from password change")
        data = await self.request.json()
        try:
            email = serializer.loads(data["token"], salt=EmailSecret.EMAIL_SALT, max_age=7200)  # 2 hour
            user = await User.get(email=email)
            password = data["password"]
        except KeyError:
            return web.json_response({"error": "You must provide token and password"}, status=400)
        except SignatureExpired:
            return web.json_response({"error": "Your link is expired"}, status=400)
        except BadTimeSignature:
            return web.json_response({"error": "Wrong token"}, status=400)
        except UserDoesNotExist:
            return web.json_response({"error": "User doesn't exist"}, status=404)

        # password validation here
        if len(password) < 3:
            return web.json_response({"error": "Password is unvalid"}, status=400)

        user.set_password(password)
        await user.save()

        return web.json_response({"msg": "Password has been changed"})
