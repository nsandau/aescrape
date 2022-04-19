FROM python:3.10-bullseye

RUN apt-get -y update && apt-get install -y chromium chromium-driver && apt-get -y autoremove && apt-get -y autoclean

RUN pip install --upgrade pip
RUN pip install selenium click pandas matplotlib python-dotenv

WORKDIR /usr/workspace 