FROM rasa/rasa-sdk:3.1.1

USER root
WORKDIR /app

# system update and configure locale
RUN apt-get update
RUN apt-get install -y locales
RUN locale-gen es_ES
RUN locale-gen es_ES.utf8

# install python requirements
COPY Docker/rasa/actions/requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --verbose -r requirements.txt

# copy email secrets
COPY secrets/email_secrets.env /app/secrets/
