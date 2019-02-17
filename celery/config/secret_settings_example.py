# USERNAME and PASSWORD used for database (from /mongodb/.env file)
USERNAME = ""
PASSWORD = ""


class SecretConfig:
    MongoURL = "mongodb://{}:{}@mongodb:27017".format(USERNAME, PASSWORD)

    # This database URI used as backend for celery tasks.
    MongoAsCeleryBackend = MongoURL + "/celery"

class EmailSecret:
    # From this email addres your application will send emails to users.
    # You need to give permissions for this in your email account preferences.
    EMAIL_ADRESS = "YOUR_EMAIL@gmail.com"
    PASSWORD = "PASSWORD_FOR_EMAIL"
