#!/bin/bash

# Set secrets
source /app/values.env

# Run rasa
rasa run -m /app/models --enable-api --cors * --debug --endpoints endpoints.yml --log-file logs/rasa.log --debug
