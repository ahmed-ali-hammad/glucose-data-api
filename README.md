<h3 align="center">glucose-data-api</h3>

<div align="center">
  <img src="https://img.shields.io/badge/status-active-success.svg" />
  <img src="https://img.shields.io/badge/python-3.13-blue" />
</div>

---

<p align="center">glucose-data-api
    <br> 
</p>

## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting-started)
- [Built Using](#built-using)

## 🧐 About <a name = "about"></a>
WIP


## 🏁 Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites
 - [Docker](https://docs.docker.com/)
 - [Docker Compose](https://docs.docker.com/compose/)

### Installing
If you're opening this project using [devcontainers](https://containers.dev/) then your docker container should be ready to go!

Otherwise you will need to start the docker compose environment `docker compose up` and open a shell into the container `glucose-data-api-dev`.

```bash
$ docker compose up
$ docker exec -it glucose-data-api-dev /bin/bash   # spawns a shell within the docker container
$ pipenv shell  # spawns a shell within the virtualenv 
```

### Database Migrations
*Note: The following three Alembic commands are useful to document here, but if you're setting up this project, you only need to run the third one: `alembic upgrade head`.*

```bash
# init the migrations folder
$ alembic init migrations  

# create a new migration version
$ alembic revision --autogenerate -m "message"  

# apply migrations
$ alembic upgrade head
```

### ▶️ Running the API
```bash
# Run the server using click
$ python cli.py run-webapp
```

Endpoints:
- [API Docs](http://localhost:7091/docs)
- [Healthcheck](http://localhost:7091/health)

### 🧪 Running the tests <a name = "tests"></a>
- [pytest](https://docs.pytest.org/) is used to run unit and integration tests.
- [schemathesis](https://schemathesis.readthedocs.io/en/stable/) is used for API testing.

```bash
# To run unit and integration tests
$ pytest .

# The server has to be running to use Schemathesis.
$ st run http://0.0.0.0:8000/openapi.json --experimental=openapi-3.1
$ st run http://0.0.0.0:8000/openapi.json --checks all --experimental=openapi-3.1   # More strict checks
``` 

### Code Style & Linting
The following tools are run during pipelines to enforce code style and quality.

 - [flake8](https://flake8.pycqa.org/en/latest/) for linting
 - [isort](https://pycqa.github.io/isort/) for import sorting
 - [black](https://black.readthedocs.io/en/stable/) for code style

### Python Package Management
- [pipenv](https://pipenv.pypa.io/en/latest/) is used to manage Python packages. 

```bash
$ pipenv shell  # spawns a shell within the virtualenv
$ pipenv install  # installs all packages from Pipfile
$ pipenv install --dev # installs all packages from Pipfile, including dev dependencies
$ pipenv install <package1> <package2>  # installs provided packages and adds them to Pipfile
$ pipenv update  # update package versions in Pipfile.lock, this should be run frequently to keep packages up to date
$ pipenv uninstall package # uninstall a package 
$ pipenv uninstall package  --categories dev-packages # uninstall a dev package
```

## ⛏️ Built Using <a name = "built_using"></a>
 - [FastAPI](https://fastapi.tiangolo.com/) - Web Framework.
 - [Uvicorn](https://www.uvicorn.org/) - ASGI web server.
 - [MySQL](https://www.mysql.com/) - Database.
 - [SQLAlchemy](https://www.sqlalchemy.org/) - ORM.
 - [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Database Migration Tool.