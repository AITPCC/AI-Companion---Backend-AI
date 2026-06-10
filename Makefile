.PHONY: db-up db-upgrade db-downgrade db-current db-history

REV ?= head
DOWN_REV ?= -1

db-up:
	docker compose up -d db

db-upgrade:
	uv run alembic upgrade $(REV)

db-downgrade:
	uv run alembic downgrade $(DOWN_REV)

db-current:
	uv run alembic current

db-history:
	uv run alembic history
