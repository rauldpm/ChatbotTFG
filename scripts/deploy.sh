#!/bin/bash

timestamp=$(date +"%Y-%m-%d-%H-%M-%S")
instance_name="server-${timestamp}"
project="your-project-name"
instance_zone="europe-southwest1-a"
instance_size="e2-small"
user=$(id -nu 1000)
repo_name="RuleChatbotTFG"
dir="/home/${user}"

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
  echo "Can not get instance ip"
  exit
fi

until $(nc -w 1 -z ${ip} 22); do
    echo "Waiting ${ip} 22"
    sleep 1
done

# Get nginx container id
nginx_container_id=$(docker ps -aqf "name=docker-compose_nginx_1")
if [[ ${nginx_container_id} == '' ]]; then
  echo "Can not get nginx container id"
  exit
fi

# Clone repo and compress it
git clone https://github.com/rauldpm/${repo_name}.git  "${dir}/${repo_name}_deploy"
cp "${dir}/${repo_name}/secrets/telegram_secrets.env" "${dir}/${repo_name}_deploy/secrets/"
cp "${dir}/${repo_name}/secrets/email_secrets.env" "${dir}/${repo_name}_deploy/secrets/"
load_balancer_ip=$(gcloud compute instances describe "your-redis-instance-name" --zone="${instance_zone}" --quiet --format='get(networkInterfaces[0].networkIP)')
sed -i "s/redis-db-ip/${load_balancer_ip}/g" "${dir}/${repo_name}_deploy/endpoints.yml"
tar -cf "${dir}/${repo_name}_deploy.tar.gz" -C "${dir}" "${repo_name}_deploy"

# Copy repo dir
gcloud compute scp "${dir}/${repo_name}_deploy.tar.gz" --project=${project} ${user}@${instance_name}:${dir} --zone=${instance_zone} --quiet
if [[ $? != "0" ]]; then
  echo "Can not copy repository into VM"
  exit
fi

rm -rf "${dir}/${repo_name}_deploy.tar.gz"
rm -rf "${dir}/${repo_name}_deploy"

# Copy rasa server deploy docker script
gcloud compute scp "${dir}/${repo_name}/scripts/deploy-rasa-docker.sh" --project=${project} ${user}@${instance_name}:${dir} --zone=${instance_zone} --quiet
if [[ $? != "0" ]]; then
  echo "Can not copy script into VM"
  exit
fi

# Run server deploy script
gcloud compute ssh --project=${project} --zone=${instance_zone} ${user}@${instance_name} -- "bash ${dir}/deploy-rasa-docker.sh"
if [[ $? != "0" ]]; then
  gcloud compute ssh --project=${project} --zone=${instance_zone} ${user}@${instance_name} -- "bash ${dir}/deploy-rasa-docker.sh"
    if [[ $? != "0" ]]; then
      echo "Can not run script into VM"
      exit
    fi
fi

# Add instance ip to load balancer
docker exec -it ${nginx_container_id} bash -c "echo 'server ${ip}:5005;' >> /etc/nginx/servers"
docker exec -it ${nginx_container_id} nginx -s reload
# Save new ip outside the container
echo "server ${ip}:5005;" >> "${dir}/${repo_name}/Docker/nginx/conf/servers"
