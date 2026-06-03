.PHONY: test up down build

up:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

build:
	docker compose -f infra/docker-compose.yml build

test:
	docker compose -f infra/docker-compose.yml exec app pytest tests/ -v