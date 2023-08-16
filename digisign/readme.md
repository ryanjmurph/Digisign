## Digisign!

### Introduction

This is the Digisign web application. A web app that allows difference devices to display announcements

### Development & Deployment

To run the application locally, you need to have the following installed:

- Docker
- Packages in requirements.txt

Before running the docker container, you need to set the following environment variables in a `.env` file. You may also copy the `.env.example` file and rename it to `.env`:

To run the docker container, run the following command:

```bash
docker-compose up
```

or

```bash
docker-compose up --build # (for clearing the build cache)
```

or through Docker Desktop

### Project Setup

#### Controller (controllers)

The controller is the main component of the application. It is responsible for routing and handling requests. It also handles the logic of the application.

#### Model (models)

The model is the component that handles the database. It is responsible for the database schema and the database queries.
