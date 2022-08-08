#!/bin/bash

user=$(id -nu 1000)
repo_name="RuleChatbotTFG"
dir="/home/${user}"

# Decompress repo
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

# Launch rasa server
cd ${dir}/${repo_name}/Docker/docker-compose
sudo docker-compose -f docker-compose-rasa.yml up --build -d