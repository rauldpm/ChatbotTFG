#!/bin/bash

# Adapted from https://github.com/RasaHQ/rasa-sdk/blob/main/entrypoint.sh

set -Eeuo pipefail

function print_help {
    echo "Available options:"
    echo " test            - Run stories tests"
    echo " data-validate   - Run nlu data validationm"
}

case ${1} in
    test)
        exec python -m rasa test
        ;;
    data-validate)
        exec python -m rasa data validate
        ;;
    *)
        print_help
        ;;
esac