lint:
	poetry run ruff check .
	poetry run mypy .

format:
	poetry run ruff check --fix .
	poetry run ruff format .

run:
	docker build -t polako-weather .
	docker run -p 8000:8000 polako-weather