.PHONY: test up down build stress

up:
	docker compose -f infra/docker-compose.db.yml up -d
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down
	docker compose -f infra/docker-compose.db.yml down

build:
	docker compose -f infra/docker-compose.yml build

test:
	docker compose -f infra/docker-compose.yml -f infra/docker-compose.test.yml run --rm app pytest tests/ -v

db-up:
	docker compose -f infra/docker-compose.db.yml up -d

db-down:
	docker compose -f infra/docker-compose.db.yml down

stress:
	uv run locust -f locustfile.py --host http://localhost:8000

# Abre Swagger automáticamente en el navegador predeterminado
docs:
	@if [ "$$(uname)" = "Darwin" ]; then \
		open http://localhost:8000/docs; \
	elif [ "$$(uname)" = "Linux" ]; then \
		if grep -q microsoft /proc/version; then \
			powershell.exe -Command "start http://localhost:8000/docs"; \
		else \
			xdg-open http://localhost:8000/docs; \
		fi; \
	fi