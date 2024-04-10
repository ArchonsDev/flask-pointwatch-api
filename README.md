# PointWatch Backend API

This is the Backend API for the PointWatch project.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)

## Installation

Open Git bash and run the following commands:

```sh
git clone https://github.com/ArchonsDev/flask-pointwatch-api.git
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
