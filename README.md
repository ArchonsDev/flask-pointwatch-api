# PointWatch Backend API

This is the Backend API for the PointWatch project.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)

## Installation

### Database Setup

Ensure you have MySQL installed.

Open Command Prompt and run the following commands:

```sh
mysql -u root -p
```

When prompted to enter a password, type the password for the root user that you have configured.

Once logged in, run the following commands:

```sh
CREATE USER 'pointwatchuser'@'%' IDENTIFIED BY 'Monabestm00sic!';

CREATE DATABASE dbpointwatch;

GRANT ALL PRIVILEGES ON dbpointwatch.* TO 'pointwatchuser'@'%';

FLUSH PRIVILEGES;
```

### API Setup

Open Git bash and run the following commands:

```sh
git clone https://github.com/ArchonsDev/flask-pointwatch-api.git
```

In the project directory, create the a `config` file with the following contents:

```py
# App Configuration
SECRET_KEY = # See config folder in PointWatch Drive
# DBMS Configuration
SQLALCHEMY_DATABASE_URI = # See config folder in PointWatch Drive
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Mailer Configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = # See config folder in PointWatch Drive
MAIL_PASSWORD = # See config folder in PointWatch Drive
```

## Usage

Navigate to the project directory and run the following command:

```sh
# Create a virtual environment (if there is none)
py -m venv .venv
# Start the virtual environment
source .venv/scripts/activate
# or
.venv/scripts/activate.bat
# or
source .venv/bin/activate
# Install prerequisites
pip install -r requirements.txt

flask run
# or (debugging enabled)
flask run --debug
```

## Migrations

When changes to the schema are made, it is necessary to perform these steps:

```sh
flask db init

flask db migrate -m "message"

flask db upgrade
```

## Support

Please [open an issue](https://github.com/ArchonsDev/flask-pointwatch-api) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/ArchonsDev/flask-pointwatch-api/compare/).
