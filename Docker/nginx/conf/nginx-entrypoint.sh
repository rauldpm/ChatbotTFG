#!/bin/sh

set -e

# allow nginx to stay in the foreground
# so that Docker can track the process properly
nginx -g 'daemon off;'
