FROM rasa/rasa:3.1.1

USER root

# copy proyect files
# the dockerfile needs to be copied to the root path
COPY actions/* /app/actions/
COPY data/* /app/data/
COPY tests/* /app/tests/
COPY config.yml credentials.yml domain.yml endpoints.yml /app/
COPY Docker/testing/entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
WORKDIR '/app'

ENTRYPOINT ["/usr/bin/entrypoint.sh"]