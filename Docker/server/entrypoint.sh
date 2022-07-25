#!/bin/bash

# Set secrets
source /app/secrets/telegram_secrets.env

# Run rasa
rasa run -m /app/models --enable-api --cors * --debug --endpoints endpoints.yml --log-file logs/rasa.log --debug
