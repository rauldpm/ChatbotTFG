# ChatbotTFG

| | | | |
|--|--|--|--|
| [![Build builder container](https://github.com/rauldpm/ChatbotTFG/actions/workflows/build-train-container.yml/badge.svg)](https://github.com/rauldpm/ChatbotTFG/actions/workflows/build-train-container.yml) | [![Build testing container](https://github.com/rauldpm/ChatbotTFG/actions/workflows/build-testing-container.yml/badge.svg)](https://github.com/rauldpm/ChatbotTFG/actions/workflows/build-testing-container.yml) | [![Build Rasa model](https://github.com/rauldpm/ChatbotTFG/actions/workflows/build-model.yml/badge.svg)](https://github.com/rauldpm/ChatbotTFG/actions/workflows/build-model.yml) | [![Tests](https://github.com/rauldpm/ChatbotTFG/actions/workflows/rasa-test.yml/badge.svg)](https://github.com/rauldpm/ChatbotTFG/actions/workflows/rasa-test.yml)

## Description

This project houses a chatbot built with the Open Source Rasa software in its version 3.1.1

The objective of this bot is to provide both establishments dedicated to hospitality and potential customers with a means to facilitate and speed up the reservation process in the establishment.

In this repository you will find the necessary code to train the chatbot as well as tools to deploy it on a local device, both directly and through Docker containers, as well as automated scripts to deploy on Google Compute Engine.

## Branches

The [branches](https://github.com/rauldpm/ChatbotTFG/branches) of this repository are structured as follows:

- main: Main branch, contains the latest validated and published version.
- x.x: Numbered branches, contain the specific development of a specific version, contain the latest version in development, for example 1.0, 2.1, 4.3

As an example of functionality, the development process would be as follows for a final version 5.5.3:

- Branch 5.5: In latest release version (5.5.2)
- Branch 5.5: Parallel development branch is created (issue_descripcion_origin), for example: 23_add_users_5.5
- Branch 23_add_users_5.5: The corresponding development is carried out.
- When finishing the development of 23_add_users_5.5, PR and merge are done after testing to 5.5
- When all the code of the 5.5 branch is finished, tag is created and released with the corresponding changelog.
- Merge from 5.5 to main.
- Production servers are updated with the new version.



## Tags and releases

The [tags](https://github.com/rauldpm/ChatbotTFG/tags) contain a specific and final version of the development, it is highly recommended to use the last tag created.

The [releases](https://github.com/rauldpm/ChatbotTFG/releases) contain a changelog regarding the immediately lower version in addition to containing the source code of said version.

## How to use it

- See the [Wiki](https://github.com/rauldpm/ChatbotTFG/wiki) section of the repository.

## How to contribute

- If you want to propose an improvement or comment on ideas, use the [Discussions](https://github.com/rauldpm/ChatbotTFG/discussions) section.
- If you have found a bug and want to report it, create an [Issue](https://github.com/rauldpm/ChatbotTFG/issues).
- In case you want to add your code contribution, keep in mind the following:
   - Read the Branches section to learn how branching works.
   - No Pull Request addressed to the main branch will be accepted.
   - Create your [Pull Requests](https://github.com/rauldpm/ChatbotTFG/pulls) to the numbered main branch you want.
   - Add a good and clear description of the changes introduced in addition to the largest number of possible tests (tests, conversations, etc)

## Licence

This project has been and is being developed under the license [GNU General Public License v3.0](https://github.com/rauldpm/ChatbotTFG/blob/main/LICENSE).