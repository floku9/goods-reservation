# goods-reservation

## Description

API that is made for reservation of goods

## Prerequisites

- Docker
- Docker Compose

## Installation and Running with Docker Compose

To set up and run the project using Docker Compose, follow these steps:

1. Clone the repository:

   ```bash
   git clone [https://github.com/floku9/goods-reservation](https://github.com/floku9/goods-reservation)
   cd goods-reservation
   ```

2. Create .env file that is suitable for your case, or just copy .env-example and delete .example part

3. Up the docker compose

    ```bash
    docker-compose up --build
    ```

After this step, the project will be available at <http://localhost:8000> (if you use default settings). Also all tests will be run and in your
local folder will be created folder called `htmlcov` with coverage report.

## Running tests without docker compose

To run tests without docker compose, you need to have installed:
    - Python 3.12
    - Poetry

If poetry not installed, install it with:

```bash
pip install poetry
```

To run tests without coverage use the following command:

```bash
poetry run pytest tests
```

To run tests with coverage use the following command:

```bash
poetry run pytest --cov=app tests
```

If you want to run tests with coverage report in file, you need to run the following command:

```bash
poetry run pytest --cov=app --cov-report html tests
```

Then in your local folder will be created folder called `htmlcov` with coverage report.
