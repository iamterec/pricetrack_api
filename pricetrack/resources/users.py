from aiohttp import web
from extensions import db
from config.secret_settings import SecretConfig, EmailSecret
import json
from aiohttp_cors import CorsViewMixin
from pymongo.errors import DuplicateKeyError
from cerberus import Validator
from models.user import User, UserDoesNotExist
import jwt
from authorization import login_required
import requests
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
        if validation:
            return web.json_response({"errors": validation[0]}, status=validation[1])

        # create user
        try:
            user = User(email=data["email"])
            user.set_password(data["password"])
            await user.save()
        except DuplicateKeyError:
            return web.json_response({"errors": {"email": ["User with this email alredy exist"]}}, status=409)

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
        await user.save()

        return web.json_response({"msg": "hello from patch"})


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
        response = requests.get(url, headers={"Authorization": "Bearer " + access_token})
        user_info = response.json()
        print(user_info)
        # manage user and generate jwt token
        try:
            user = await User.get(email=user_info["email"])
        except UserDoesNotExist:
            print("User doesnt exist")
            user = User(email=user_info["email"], username=user_info["name"],
                        avatar=user_info["picture"])
            random_str = generate_random_string(14)
            user.set_password(random_str)
            user_id = await user.save()
            jwt_token = jwt.encode({"user_id": str(user_id)}, SecretConfig.JWT_SECRET)
        else:
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
        send_reset_link.delay(data["email"], token)
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


class Hello(web.View, CorsViewMixin):

    async def get(self):
        document = await db.test_collection.find_one({}, {"_id": 0})
        print(document)
        return web.Response(text=json.dumps(document))
