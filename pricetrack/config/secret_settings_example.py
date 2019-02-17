# USERNAME and PASSWORD used for database (from /mongodb/.env file)
USERNAME = ""
PASSWORD = ""


class SecretConfig:
    MongoURL = "mongodb://{}:{}@mongodb:27017".format(USERNAME, PASSWORD)

    # This database URI used as backend for celery tasks.
    MongoAsCeleryBackend = MongoURL + "/celery"

    SECRET = "SUPER SECRET KEY"
    JWT_SECRET = "SUPER SECRET JWT KEY"


class EmailSecret:
    # Keys that are used to generate a token when user change password.
    EMAIL_SECRET_KEY = "SUPER SECRET EMAIL KEY"
    EMAIL_SALT = "EMAIL SALT"
