FROM rasa/rasa:3.1.1

USER root

# Copy proyect files
COPY actions/* /app/actions/
COPY data/* /app/data/
COPY config.yml credentials.yml domain.yml endpoints.yml values.env /app/
COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
WORKDIR '/app'

# Neccesary to run the server inside the docker container
RUN sed -i "s/localhost:5055/action_server:5055/g" endpoints.yml

# Train and run
RUN rasa train
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
