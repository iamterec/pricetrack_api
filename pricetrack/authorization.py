import jwt
from aiohttp import web
from bson import ObjectId
from config.secret_settings import SecretConfig
from models.user import User, UserDoesNotExist


def login_required(func):
    async def wrapper(request):
        if not request.request.user:
            return web.json_response({'msg': 'Authorization required'}, status=401)
        return await func(request)
    return wrapper


@web.middleware
async def auth_middleware(request, handler):
    request.user = None
    jwt_token = request.headers.get('authorization', None)
    if jwt_token:
        try:
            payload = jwt.decode(jwt_token, SecretConfig.JWT_SECRET, algorithms=["HS256"])
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return web.json_response({'message': 'Token is invalid'}, status=400)

        try:
            # get the User and set it to the request object
            request.user = await User.get(_id=ObjectId(payload['user_id']),
                                          db=request.app["db"])
        except UserDoesNotExist:
            return web.json_response({'message': 'Token is invalid'}, status=400)
    resp = await handler(request)
    return resp
