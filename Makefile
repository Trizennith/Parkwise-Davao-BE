.PHONY: help install run test migrate makemigrations shell clean docker-build docker-run docker-stop docker-logs app.local.build 

ifneq (,$(wildcard .env.local))
    include .env.local
    export
endif

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
	pip install daphne

run:
	$(MANAGE) runserver

run-ws:
	daphne -b 0.0.0.0 -p 8000 app.config.asgi:application

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
app.local.build:
	@docker compose -f ./docker/app.local.yml build --no-cache --force-rm
	@docker compose -f ./docker/app.local.yml up -d

app.local.run:
	@echo "Starting docker compose stack: $(DOCKER_COMPOSE_LOCAL_NAME)-backend-1..."
	@docker compose -p $(DOCKER_COMPOSE_LOCAL_NAME) up -d

app.local.down: 
	@echo "Stopping docker compose stack: $(DOCKER_COMPOSE_LOCAL_NAME)-backend-1..."
	@docker compose -p $(DOCKER_COMPOSE_LOCAL_NAME) down

docker-logs:
	@echo "Viewing logs for $(DOCKER_COMPOSE_LOCAL_NAME)-backend-1..."
	@docker compose -p $(DOCKER_COMPOSE_LOCAL_NAME) logs -f backend

app.local.seed: 
	@echo "Seeding database..."
	@docker exec -it $(DOCKER_COMPOSE_LOCAL_NAME)-backend-1 python manage.py seed_data

app.local.db.build:
	@docker compose -f ./docker/app.local.db.yml build --no-cache --force-rm
	@docker compose -f ./docker/app.local.db.yml up -d

app.local.db.down:
	@docker compose -f ./docker/app.local.db.yml down

run.local:
	@echo "Starting the local development environment..."
	@docker compose -f ./docker/app.local.db.yml up -d
	@. ./venv/bin/activate && python manage.py runserver

run:
	@. ./venv/bin/activate && python manage.py runserver

app.local.test:
	@./scripts/run_tests.sh   
	


check.docker.compose-stack:
ifndef $(DOCKER_COMPOSE_LOCAL_NAME)
	$(error DOCKER_COMPOSE_LOCAL_NAME is undefined. Use: make "<command>" DOCKER_COMPOSE_LOCAL_NAME=<DOCKER_COMPOSE_LOCAL_NAME>)
endif
