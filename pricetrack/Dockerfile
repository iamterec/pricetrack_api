FROM python:3.6-alpine

ENV INSTALL_PATH /pricetrack
RUN mkdir -p INSTALL_PATH 

WORKDIR $INSTALL_PATH

# some stuff for psycopg instalation
RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers libffi-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# delete some stuff after psycorg instalation
RUN apk del .build-deps gcc musl-dev linux-headers libffi-dev

