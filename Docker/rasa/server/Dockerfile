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

# neccesary to run the server inside the docker container
RUN sed -i "s/localhost:5055/action_server:5055/g" endpoints.yml

# download pre-trained model
RUN curl -sO https://storage.googleapis.com/tfg-rasa-models/model.tar.gz
RUN mkdir models
RUN mv model.tar.gz models/

# run rasa
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
