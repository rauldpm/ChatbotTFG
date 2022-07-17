FROM rasa/rasa-sdk:3.1.1

USER root
WORKDIR /app

RUN apt-get update
RUN apt-get install -y locales

RUN locale-gen es_ES
RUN locale-gen es_ES.utf8

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --verbose -r requirements.txt

EXPOSE 5055
USER 1001