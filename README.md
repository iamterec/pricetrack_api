# Pricetrack API
This is an API for Pricetrack application.<br>
[Client for this application can be found here](https://github.com/iamterec/pricetrack_ui)

## About Pricetrack
This application will allow you to track some numeric information from third party sites.
You just need to fill page url and css selector and application will parce matched numeric information every hour and save to database.
You will able to see this information in graph and table.

## Used technologies
The application based on [Aiohttp](https://github.com/aio-libs/aiohttp).
It also uses [Docker](https://www.docker.com/), [Docker-compose](https://github.com/docker/compose), [Celery](http://www.celeryproject.org/), [MongoDB](https://www.mongodb.com/) and [Swagger](https://github.com/swagger-api/swagger-ui)(unfinished)

## How to run this
To be able to run this application you need installed Docker and Docker Compose.

#### Make database initialization:
Rename *`.env_example`*  file in *`/mongodb`* to *`.env`* and fill USERNAME and PASSWORD<br>

Then in one terminal window run:
```shell
docker-compose up mongodb
```
In another one:
```shell
docker exec -it price_tracker_mongodb_1 sh -c "mongo --eval \"var password = '\$MONGO_INITDB_ROOT_PASSWORD'; var username = '\$MONGO_INITDB_ROOT_USERNAME'\" /data/db/initDB.js"
```


#### Fill username and password:
Then rename those files and fill USERNAME and PASSWORD (same as in previous step):<br>

*`secret_settings_example.py`* file in *`pricetrack/config/`* to *`secret_settings.py`*<br>
*`secret_settings_example.py`* file in *`celery/config/`* to *`secret_settings.py`*<br>

#### Then finaly run:
```shell
docker-compose up
```
Now API should work and you can use it.
