FROM python:3.12-slim

ARG COMMIT_HASH=unknown
ENV COMMIT_HASH=${COMMIT_HASH}

WORKDIR /code

COPY pyproject.toml poetry.lock* /code/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main

COPY . /code

CMD ["uvicorn", "app.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
