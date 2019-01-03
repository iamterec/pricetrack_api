from config.secret_settings import SecretConfig
from aiohttp import web
from models.user import User
import jwt
from bson import ObjectId


def login_required(func):
    async def wrapper(request):
        if not request.request.user:
            return web.json_response({'msg': 'Auth required'}, status=401)
        return await func(request)
    return wrapper


@web.middleware
async def auth_middleware(request, handler):
    request.user = None
    jwt_token = request.headers.get('authorization', None)
    if jwt_token:
        try:
            payload = jwt.decode(jwt_token, SecretConfig.JWT_SECRET)
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return web.json_response({'message': 'Token is invalid'}, status=400)

        # request.user = User.objects.get(id=payload['user_id'])
        request.user = await User.get(_id=ObjectId(payload['user_id']))
    resp = await handler(request)
    return resp
