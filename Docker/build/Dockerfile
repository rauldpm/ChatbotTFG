FROM rasa/rasa:3.1.1

USER root

# copy proyect files
# the dockerfile needs to be copied to the root path
COPY . /app/
WORKDIR '/app'

# train model
ENTRYPOINT  ["rasa", "train"]
##