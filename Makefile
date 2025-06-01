.PHONY: help install run test migrate makemigrations shell clean docker-build docker-run docker-stop docker-logs

# Variables
DOCKER_COMPOSE = docker compose
PYTHON = python3
MANAGE = $(PYTHON) manage.py

help:
	@echo "Available commands:"
	@echo "  make install    - Install project dependencies"
	@echo "  make run        - Run the development server"
	@echo "  make test       - Run tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make shell      - Open Django shell"
	@echo "  make clean      - Clean Python cache files"
	@echo "  make docker-build - Build Docker containers"
	@echo "  make docker-run   - Run Docker containers"
	@echo "  make docker-stop  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker container logs"

# Django commands
install:
	pip install -r requirements.txt

run:
	$(MANAGE) runserver

test:
	$(MANAGE) test

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

shell:
	$(MANAGE) shell

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +

# Docker commands
docker-build:
	$(DOCKER_COMPOSE) build

docker-run:
	$(DOCKER_COMPOSE) up -d

docker-stop:
	$(DOCKER_COMPOSE) down

docker-logs:
	$(DOCKER_COMPOSE) logs -f 