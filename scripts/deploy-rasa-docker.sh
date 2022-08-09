#!/bin/bash

# It is recommended to configure your firewall according to your requisites
# Needed ports
# - rasa actions: 5055
# - rasa server: 5005 (need to be open to accept bot requests)
# - redis db: 6379
# - smtp (your smtp port)

# This deployment it is designed to accept connections from:
# - nginx load balancer instance (incomming connections in 5005)
# - redis db instance (incoming and  outgoing connections in 6379)
# - Allow connections with telegram api

user=$(id -nu 1000)
repo_name="ChatbotTFG"
dir="/home/${user}"

# Extract repository
tar -xf ${dir}/${repo_name}*.tar.gz
mv ${dir}/${repo_name}*/ "${dir}/${repo_name}"
rm -rf ${dir}/${repo_name}*.tar.gz

# Install docker and docker-compose
curl -sSL https://get.docker.com/ | sh
curl -fsSL https://get.docker.com/rootless | sh
sudo apt -y install docker-compose

# Start docker service
sudo systemctl start docker
sudo systemctl enable docker

# Launch rasa server in detached mode
cd ${dir}/${repo_name}/Docker/docker-compose
sudo docker-compose -f docker-compose-rasa.yml up --build -d
