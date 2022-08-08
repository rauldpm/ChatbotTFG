#!/bin/bash

project="your-project-name"
instance_zone="your-instance-zone" # eg: europe-southwest1-a
instance_size="your-instance-type" # eg: e2-small
repo_name="ChatbotTFG"
user=$(id -nu 1000)
dir="/home/${user}"

# Get deployed servers count
servers_count=$(gcloud compute instances list | grep -o 'server' | wc -l)

if [[ ${servers_count} -gt 1 ]]; then
  # Get newest server
  servers=($(gcloud compute instances list | grep -i -E -o "server[0-9\-]*"))
  newest=${servers[-1]}
  ip=$(gcloud compute instances describe "${newest}" --zone="${instance_zone}" --quiet --format='get(networkInterfaces[0].networkIP)')

  # Delete
  gcloud compute instances delete ${newest} --zone="${instance_zone}" --delete-disks="all" --quiet

  # Wait until the instance is fully destroyed
  # The previous gcloud command should wait until it is destroyed
  # It is better to make sure that the last instance is different from the deleted one
  actual=${newest}
  until [ ${actual} != ${newest} ]; do
    servers=($(gcloud compute instances list | grep -i -E -o "server[0-9\-]*"))
    actual=${servers[-1]}
    sleep 5
  done

  # Remove ip from load balancer upstream list
  nginx_container_id=$(docker ps -aqf "name=nginx")
  docker exec -it ${nginx_container_id} bash -c "sed -i '/server ${ip}:5005;/d' /etc/nginx/servers"
  docker exec -it ${nginx_container_id} nginx -s reload
  # Remove server ip in case the docker container is lost
  sed -i "/server ${ip}:5005;/d" "${dir}/${repo_name}/Docker/nginx/conf/servers"
fi
