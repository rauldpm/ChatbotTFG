FROM rasa/rasa:3.1.1

USER root

# copy proyect files
COPY actions/* /app/actions/
COPY data/* /app/data/
COPY secrets/telegram_secrets.env /app/secrets/
COPY config.yml credentials.yml domain.yml endpoints.yml /app/
COPY Docker/rasa/server/entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
WORKDIR '/app'

# train model
ENTRYPOINT  ["rasa", "train"]
