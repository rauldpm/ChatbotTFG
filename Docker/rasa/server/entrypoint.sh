#!/bin/bash

# set secrets
source /app/secrets/telegram_secrets.env

# run rasa
rasa run -m /app/models --enable-api --cors * --debug --endpoints endpoints.yml --credendials credentials.yml --log-file logs/rasa.log --debug
