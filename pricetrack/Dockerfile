FROM python:3.6-alpine

ENV INSTALL_PATH /pricetrack
RUN mkdir -p INSTALL_PATH 

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

