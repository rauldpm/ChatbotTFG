#!/bin/bash

user=$(id -nu 1000)
repo_name="RuleChatbotTFG"
dir="/home/${user}/${repo_name}"

# Get number of active connections to rasa servers
active_connections=$(docker exec -it docker-compose_nginx_1 curl localhost/nginx_status | grep "Active connections" | awk '{print $3}')
# Get numbber of connections when the last server were deployed or destroyed
last_active_connections=$(cat ${dir}/scripts/last_active.txt)
# Get number of rasa server (each server will handle 10 users)
servers=$(gcloud compute instances list | grep -o 'server' | wc -l)

# Deploy server if the active connections are greater than 10*(server_count)
if [[ ${active_connections} -gt $((${servers}*10)) ]]; then
  while [[ ${active_connections} -gt ${servers}*10 ]]; do
    bash "${dir}/scripts/deploy.sh"
    servers=$(gcloud compute instances list | grep -o 'server' | wc -l)
  done
# Delete servers
elif [[ ${active_connections} -lt $(((${servers}+1)*10)) ]]; then
  while [ ${active_connections} -lt $(((${servers}+1)*10)) ]; do
    bash "${dir}/scripts/destroy.sh"
    servers=$(gcloud compute instances list | grep -o 'server' | wc -l)
  done
else
  echo "A"
fi