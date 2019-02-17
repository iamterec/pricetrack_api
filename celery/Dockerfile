FROM python:3.6-alpine

RUN adduser -S celery_user

ENV CELERY_PATH /celery
RUN mkdir -p CELERY_PATH

WORKDIR $CELERY_PATH
# COPY ./tasks $CELERY_PATH/tasks

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# RUN pip install celery pymongo requests beautifulsoup4
