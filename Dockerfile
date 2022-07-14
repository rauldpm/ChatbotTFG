FROM rasa/rasa:3.1.1


USER root
COPY . /app
WORKDIR '/app'

# Neccesary to run the server inside the docker container
RUN sed -i "s/localhost:5055/action_server:5055/g" endpoints.yml

RUN rasa train
CMD ["run", "-m", "/app/models", "--enable-api", "--cors", "*", "--debug", "--endpoints", "endpoints.yml", "--log-file", "logs/rasa.log", "--debug"]
