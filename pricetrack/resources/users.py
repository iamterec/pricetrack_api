from aiohttp import web
from extensions import db
from config.secret_settings import SecretConfig
import json
from aiohttp_cors import CorsViewMixin
from pymongo.errors import DuplicateKeyError
from cerberus import Validator
from models.user import User, UserDoesNotExist
import jwt


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



class Hello(web.View, CorsViewMixin):

    async def get(self):
        document = await db.test_collection.find_one({}, {"_id": 0})
        print(document)
        return web.Response(text=json.dumps(document))
