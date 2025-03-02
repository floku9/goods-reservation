FROM python:3.12-slim

RUN pip install poetry

WORKDIR /goods_reservation
COPY pyproject.toml poetry.lock /goods_reservation/
RUN poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
