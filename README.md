# goods-reservation

## Description

API that is made for reservation of goods

### Common installation steps

1. Clone the repository:

   ```bash
   git clone https://github.com/floku9/goods-reservation
   cd goods-reservation
   ```

2. Create .env file that is suitable for your case, or just copy .env-example and delete -example part

## Running with Docker Compose

### Prerequisites

- Docker
- Docker Compose

To run the project with Docker Compose, follow these additional steps:

1. Up the docker compose

    ```bash
    docker-compose up --build
    ```

After this step, the project will be available at <http://localhost:8000> (if you use default settings). Also all tests will be run and in your
local folder will be created folder called `htmlcov` with coverage report.

## Running tests without docker compose

### Prerequisites

- Python 3.12
- Poetry

### If poetry not installed, install it with

```bash
pip install poetry
```

1. To run tests without coverage use the following command:

    ```bash
    poetry run pytest tests
    ```

2. To run tests with coverage use the following command:

    ```bash
    poetry run pytest --cov=app tests
    ```

3. If you want to run tests with coverage report in file, you need to run the following command:

    ```bash
    poetry run pytest --cov=app --cov-report html tests
    ```

    Then in your local folder will be created folder called `htmlcov` with coverage report.
