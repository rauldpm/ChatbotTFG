FROM rasa/rasa-sdk:3.1.1
WORKDIR /app
COPY requirements.txt requirements.txt
USER root

RUN pip install --upgrade pip
RUN pip install --verbose -r requirements.txt

RUN apt-get update && apt-get install -y locales
RUN locale-gen es_ES
RUN locale-gen es_ES.utf8

EXPOSE 5055
USER 1001