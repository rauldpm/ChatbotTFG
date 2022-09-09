This repository is made up of the following main files and folders:

- [.github](#id1)
- [.gitignore](#id2)
- [Docker](#id3)
- [actions](#id4)
- [data](#id5)
- [scripts](#id6)
- [secrets](#id7)
- [tests](#id8)
- [LICENSE](#id9)
- [README.md](#id10)
- [config.yml](#id11)
- [credentials.yml](#id12)
- [domain.yml](#id13)
- [endpoints.yml](#id14)

An explanation of each of these sections is given below.

## .github <a name="id1"></a>

This folder contains tools related to GitHub, under the workflows folder you can find files related to automatic processes when relating certain actions on GitHub.

- build-model.yml:
  - It is executed when a Rasa component is modified, such as stories.
  - When a Pull Request is merged into the main branch, if these files have been modified, the chatbot is trained, generating a file called model.tar.gz, which is uploaded to Google Compute Storage to be used by other automated processes, such as deploying servers or performing tests.

- build-testing-container.yml
  - Create an image with which the chatbot tests are performed.
  - It is hosted on DockerHub.

- build-train-container.yml
  - Creates an image with which the chatbot training is carried out, in a way that reduces processing times.
  - It is hosted on DockerHub.

- rasa-test.yml
  - Run the rasa tests using the test container hosted on DockerHub.
  - Perform NLU validation tests and histories.



## .gitignore <a name="id2"></a>

Git's own file, contains references to files or folders that should not be followed by Git, so they should not be uploaded to the GitHub repository.

Some examples of these files are database files (.db), test results (restuls), certificate files (.pem)

## Docker <a name="id3"></a>

Folder that contains everything related to development using Docker, such as Dockerfiles or files used in Docker deployment. Contains:

- build: Stores the Dockerfile used to build the image through which the chatbot is trained.

- docker-compose: Stores yml files to deploy various related services:
  - docker-compose-nginx.yml: Deploy a container with the Nginx load balancer.
  - docker-compose-rasa-nginx.yml: Deploys three containers, an Nginx load balancer, the Rasa server, and the Rasa actions server.
  - docker-compose-rasa.yml: Deploys two containers, the Rasa server and the Rasa actions server.
  - docker-compose-redis.yml: Deploy a container containing an in-memory database using Redis.

- nginx: Contains files necessary for the deployment of the Nginx container, such as the location of the certificates (read [README.md](https://github.com/rauldpm/ChatbotTFG/tree/main/Docker/nginx/certs)), as configuration files.

- rasa: Contains files needed to build Rasa server containers and Rasa actions.

- test: Contains necessary files to build a container in which to perform the Rasa test.

## actions <a name="id4"></a>
Folder containing Python classes and files needed for custom actions.

- classes: Contains the Python classes necessary to perform actions such as slot validation and custom actions such as data query or email sending.
- data: Information in json format used as an example of a DB.

## data <a name="id5"></a>

Folder that stores stories, rules, and NLUs of the chatbot.

- core: Contains files in yml format corresponding to histories. Each story represents a possible conversation with the user. They are also used to internally build additional stories derived from each other.
- nlu: Contains the NLU of the chatbot, specifies the intents (user interaction), specifying possible messages that this can send, classifying them, so that two phrases can refer to the same context. It also reflects what values ​​the chatbot should extract when parsing the phrase and where to store them.
- rules.yml: Contains simple iteration rules, so that they comply with the question-answer process and do not have a continuity of conversation beyond the question asked.

## scripts <a name="id6"></a>

Folder that stores bash shell scripts used for automated deployment of Rasa servers from the instance containing the Nginx load balancer.

- check_active_users.sh: According to active users, it deploys or removes Rasa servers.
- crontab.txt: Example of crontab used to periodically execute the previous script.
- deploy_destroy.sh: Used to destroy instances that store Rasa servers.
- deploy-rasa-docker.sh: Script used in the deployed instance to provision it with the Rasa servers.
- deploy.sh: Used to deploy instances and provision them with the above script.

## secrets <a name="id7"></a>

This folder contains two files where the credentials must be specified to access the Telegram bot and be able to send emails.

- email_secrets.env: Specifies credentials of the smtp server used to send emails to users.
- telegram_secrets.env: Specifies credentials to be able to connect with the Telegram bot.

These files should not be published in the repository other than as an example.

## tests <a name="id8"></a>

Stores user stories used for testing those stories.

## LICENSE <a name="id9"></a>

Sets the project license.

## README.md <a name="id10"></a>

General information file displayed in the repository.

## config.yml <a name="id11"></a>

Sets the configuration according to which the chatbot model is trained.

## credentials.yml <a name="id11"></a>

Set the necessary credentials to connect to different chat endpoints like Telegram. It has been configured so that credentials are set in files in the secrets folder, and these are exported as environment variables on the system.

## domain.yml <a name="id12"></a>

Main file of the project, specifies the entities that the chatbot is going to recognize, the slots where the data for each entity is stored, the forms necessary to extract and validate the slots through the Rasa server and the answers that the chatbot can give to the Username.

## endpoints.yml <a name="id13"></a>

Set endpoints as the Rasa database to use.