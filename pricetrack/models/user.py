from extensions import db
from bcrypt import hashpw, checkpw, gensalt


class UserDoesNotExist(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


class User:
    def __init__(self, email=None, username=None, avatar=None):
        self.data = {}
        self.data["email"] = email
        if username: self.data["username"] = username
        if avatar: self.data["avatar"] = avatar

    @classmethod
    async def get(cls, **kwargs):
        # print(kwargs)
        result = await db.users.find_one(kwargs)
        if not result:
            raise UserDoesNotExist("User not foud", "User does not exist")
        user = User(email=result["email"])
        user.data.update(result)
        return user

    def set_password(self, password):
        self.data["password"] = hashpw(password.encode(), gensalt())

    def check_password(self, password):
        return checkpw(password.encode(), self.data["password"])
        # return check_password_hash(self.data["password"], password)

    async def save(self):
        # if user exist
        if self.data.get("_id", None):
            user_filter = {"_id": self.data["_id"]}
            update_data = {key: value for key, value in self.data.items() if key != "_id"}
            result = await db.users.update_one(user_filter, {"$set": update_data})
            print("Save user result: ", result.raw_result)
        # if new user
        else:
            print("Insert user".center(40, "="))
            result = await db.users.insert_one(self.data)
            return result.inserted_id

    def get_dict(self):
        data = {}
        data["email"] = self.data["email"]
        if self.data.get("_id", None):
            data["_id"] = str(self.data["_id"])
        if self.data.get("avatar", None):
            data["avatar"] = self.data["avatar"]
        if self.data.get("username", None):
            data["username"] = self.data["username"]
        return data
