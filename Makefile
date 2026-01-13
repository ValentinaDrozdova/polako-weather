COMMIT_HASH=$(shell git rev-parse --short HEAD)

lint:
	poetry run ruff check .
	poetry run mypy .

format:
	poetry run ruff check --fix .
	poetry run ruff format .

run:
	docker build --build-arg COMMIT_HASH=$(COMMIT_HASH) -t polako-weather .
	docker run -p 8000:8000 polako-weather

put_version:
	@echo $(COMMIT_HASH)
