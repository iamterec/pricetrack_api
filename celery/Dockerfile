FROM python:3.6-alpine

ENV CELERY_PATH /celery
RUN mkdir -p CELERY_PATH

WORKDIR $CELERY_PATH
# COPY ./tasks $CELERY_PATH/tasks

RUN pip install celery pymongo requests beautifulsoup4
