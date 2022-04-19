FROM python:3.10-bullseye

RUN apt-get -y update
RUN apt-get install -y chromium chromium-driver

RUN pip install --upgrade pip
RUN pip install cryptography selenium click schedule pandas matplotlib python-dotenv
