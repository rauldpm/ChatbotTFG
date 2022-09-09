1. [Clone repository](#id1)
2. [Deployment](#id2)
   * [Deploy Rasa on local](#id3)
   * [Deploy Rasa on local using Docker](#id4)
   * [Deploy Nginx](#id5)
   * [Deploy Redis database](#id6)
   * [Deploy on Google Compute Engine](#id7)

---

## Clone repository <a name="id1"></a>


To perform a local deployment of the chatbot you need to download the repository of
GitHub using the command:

- git clone https://github.com/rauldpm/ChatbotTFG.git

Once cloned, it is necessary to access the chatbot directory:

- cd ChatbotTFG

Now you have different deployment options (a Telegram bot created by BotFather is required)

## Deployment <a name="id2"></a>


In this section you will find different types of deployment, choose the one that most interests you.


### Deploy Rasa on local <a name="id3"></a>

This deployment describes the steps required to run Rasa servers
on your local machine directly:

- Configure your database in the `endpoints.yml` file, in case you don't
you have your own Redis database you can deploy a container
using docker-compose.

- If you do not have your own database, run this command inside the `Docker/docker-
compose` path:

```
docker-compose -f docker-compose-redis.yml
```

- Configure the access credentials to your Telegram bot in the file
`credentials.yml`.

- Before starting the Rasa server it is necessary to train the chatbot, for this
run: `rasa train`.

- Now in a terminal execute the command: `rasa run actions` to execute the
action server.

- Execute in another terminal the command: `rasa shell`, to start the server
Rasa.


### Deploy Rasa on local using Docker <a name="id4"></a>

Configure the access credentials to your Telegram bot in the
`secrets/telegram_secrets.env` file.

- Configure the credentials of your smtp server in the
`secrets/email_secrets.env` file.

- Run the Redis database container.

```
docker-compose -f docker-compose-redis.yml up --build
```

- Configure the IP of the Redis database in the `endpoints.yml` file.

- Run the Rasa server container and Rasa actions.

```
docker-compose -f docker-compose-rasa.yml up --build
```

### Deploy Nginx <a name="id5"></a>

In case you want to use a load balancer, a docker-compose-nginx.yml file is provided through which a container with Nginx is deployed. You must ensure that all requests are made to the container instead of the server or servers.

For security, it is necessary to have two self-signed certificates with letsencrypt
associated with a DNS corresponding to the machine where Nginx is deployed.

- Place in `Docker/nginx/certs/` your certificates with the name of
`fullchain.pem` and `privkey.pem`

- Modify the `Docker/nginx/conf/servers` file by entering the IP of your
rasa's servant

- Start the Nginx service using docker-compose:

```
docker-compose -f docker-compose-nginx.yml up --build
```

The load balancer also acts as a reverse proxy, allowing all
connections are made via https.

### Deploy Redis database <a name="id6"></a>

If you don't have your own database for the Rasa server, you can
perform a quick deployment of a container with this database.

To do this, navigate to the `Docker/docker-compose/` directory and follow the
Next steps:

- Modify the docker-compose-redis.yml file by changing `redis-password`
by the password established in the `endpoints.yml` file.

- Build and start the container:

```
docker-compose -f docker-compose-redis.yml up --build
```
