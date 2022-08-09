#!/bin/bash

max_users_server=100
user=$(id -nu 1000)
repo_name="ChatbotTFG"
dir="/home/${user}/${repo_name}"

# Get number of active connections to rasa servers
active_connections=$(docker exec -it nginx curl localhost/nginx_status | grep "Active connections" | awk '{print $3}')
# Get number of rasa server (each server will handle 10 users)
servers=$(gcloud compute instances list | grep -o 'server' | wc -l)

# Deploy server if the active connections are greater than (max_users)*(server_count)
if [[ ${active_connections} -gt $((${servers}*${max_users_server})) ]]; then
  while [[ ${active_connections} -gt $((${servers}*${max_users_server})) ]]; do
    bash "${dir}/scripts/deploy.sh"
    servers=$(gcloud compute instances list | grep -o 'server' | wc -l)
  done
# Delete servers
elif [[ ${active_connections} -lt $((${servers}*${max_users_server})) ]]; then
  # The difference between the total capacity and the active connections has to be lower than ${max_users_server}
  # This will allow to fit the servers to the current capacity
  while [[ $(($((${servers}*${max_users_server})) - ${active_connections})) -gt ${max_users_server} ]]; do
    # One server has to be available ever
    if [[ ${servers} == 1 ]]; then
      break
    fi

    bash "${dir}/scripts/destroy.sh"
    servers=$(gcloud compute instances list | grep -o 'server' | wc -l)

  done
fi
