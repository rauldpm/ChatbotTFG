FROM rasa/rasa-sdk:3.1.1

USER root
WORKDIR /app

RUN apt-get update
RUN apt-get install -y locales
RUN locale-gen es_ES
RUN locale-gen es_ES.utf8

# Install python requirements
COPY Docker/actions/requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --verbose -r requirements.txt

# Copy email secrets
COPY secrets/email_secrets.env /app/secrets/

EXPOSE 5055
USER 1001