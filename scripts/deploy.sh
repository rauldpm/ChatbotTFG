#!/bin/bash

project="your-project-name"
timestamp=$(date +"%Y-%m-%d-%H-%M-%S")
instance_name="server-${timestamp}"
instance_zone="your-instance-zone" # eg: europe-southwest1-a
instance_size="your-instance-type" # eg: e2-small
user=$(id -nu 1000)
repo_name="ChatbotTFG"
dir="/home/${user}"
redis-password="the-password-of-redis-db" # Change this by your password, by default it will be used as password

# Create instance
output=$(gcloud compute instances create ${instance_name} --project=${project} --zone=${instance_zone} --machine-type=${instance_size} --network-interface=network-tier=PREMIUM,subnet=default --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=741352664526-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --tags=http-server,https-server --create-disk=auto-delete=yes,boot=yes,device-name=asd,image=projects/debian-cloud/global/images/debian-11-bullseye-v20220719,mode=rw,size=10,type=projects/${project}/zones/${instance_zone}/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any)
if [[ "ERROR" == *"${output}"* ]]; then
  echo "Failed creating instance"
  echo ${output}
  exit
fi

# Get private ip of created instance
ip=$(gcloud compute instances describe "${instance_name}" --zone="${instance_zone}" --quiet --format='get(networkInterfaces[0].networkIP)')
if [[ ${ip} == '' ]]; then
  echo "Can not get instance ip."
  echo "Destroying instance."
  gcloud compute instances delete ${instance_name} --zone="${instance_zone}" --delete-disks="all" --quiet
  exit
fi

# Wait 2 minutes to get response from server
count=0
timeout=false
until $(nc -z ${ip} 22); do
        if [[ ${count} == 120 ]]; then
                timeout=true
                break
        fi
        echo "Waiting to ssh to be available. Sleeping 10 seconds."
        count=$((${count} + 10))
        sleep 10
done

if [ ${timeout} == true ]; then
  echo "Could not connect to ssh 22 port."
  echo "Destroying instance."
  gcloud compute instances delete ${instance_name} --zone="${instance_zone}" --delete-disks="all" --quiet
  exit
fi

# Get nginx container id
nginx_container_id=$(docker ps -aqf "name=nginx")
if [[ ${nginx_container_id} == '' ]]; then
  echo "Could not get nginx container id"
  exit
fi

# Clone repo and compress it
git clone https://github.com/rauldpm/${repo_name}.git  "${dir}/${repo_name}_deploy"
cp "${dir}/${repo_name}/secrets/telegram_secrets.env" "${dir}/${repo_name}_deploy/secrets/"
cp "${dir}/${repo_name}/secrets/email_secrets.env" "${dir}/${repo_name}_deploy/secrets/"
redis_instance_ip=$(gcloud compute instances describe "your-redis-instance-name" --zone="${instance_zone}" --quiet --format='get(networkInterfaces[0].networkIP)')
sed -i "s/redis-db-ip/${redis_instance_ip}/g" "${dir}/${repo_name}_deploy/endpoints.yml"
# Change redis-password by the password specified in the redis docker-compose file
sed -i "s/redis-password/${redis_password}/g" "${dir}/${repo_name}_deploy/endpoints.yml"
sed -i "s/redis-password/${redis_password}/g" "${dir}/${repo_name}_deploy/Docker/docker-compose/docker-compose-redis.yml"
tar -cf "${dir}/${repo_name}_deploy.tar.gz" -C "${dir}" "${repo_name}_deploy"

# Copy repo dir
gcloud compute scp "${dir}/${repo_name}_deploy.tar.gz" --project=${project} ${user}@${instance_name}:${dir} --zone=${instance_zone} --quiet
if [[ $? != "0" ]]; then
  echo "Could not copy repository into VM"
  rm -rf "${dir}/${repo_name}_deploy.tar.gz"
  rm -rf "${dir}/${repo_name}_deploy"
  exit
fi

# Clean files
rm -rf "${dir}/${repo_name}_deploy.tar.gz"
rm -rf "${dir}/${repo_name}_deploy"

# Copy rasa server docker deploy script
gcloud compute scp "${dir}/${repo_name}/scripts/deploy-rasa-docker.sh" --project=${project} ${user}@${instance_name}:${dir} --zone=${instance_zone} --quiet
if [[ $? != "0" ]]; then
  echo "Could not copy script into VM"
  exit
fi

# Run server deploy script
gcloud compute ssh --project=${project} --zone=${instance_zone} ${user}@${instance_name} -- "bash ${dir}/deploy-rasa-docker.sh"
# Sometimes docker service does not start correctly, this will force the reinstall
if [[ $? != "0" ]]; then
  gcloud compute ssh --project=${project} --zone=${instance_zone} ${user}@${instance_name} -- "bash ${dir}/deploy-rasa-docker.sh"
  if [[ $? != "0" ]]; then
    echo "Can not run script into VM"
    exit
  fi
fi

# Wait until rasa server is fully deployed
count=0
timeout=false
until $(nc -z ${ip} 5005); do
        if [[ ${count} == 300 ]]; then
                timeout=true
                break
        fi
        echo "Waiting to rasa server to be available. Sleeping 10 seconds."
        count=$((${count} + 10))
        sleep 10
done

if [ ${timeout} == true ]; then
  echo "Could not connect to rasa server 5005 port."
  echo "Destroying instance."
  gcloud compute instances delete ${instance_name} --zone="${instance_zone}" --delete-disks="all" --quiet
  exit
fi

# Add instance ip to load balancer
docker exec -it ${nginx_container_id} bash -c "echo 'server ${ip}:5005;' >> /etc/nginx/servers"
docker exec -it ${nginx_container_id} nginx -s reload
# Save new ip outside the container
echo "server ${ip}:5005;" >> "${dir}/${repo_name}/Docker/nginx/conf/servers"
