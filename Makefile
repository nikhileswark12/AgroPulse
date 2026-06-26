.PHONY: setup dev build up down logs shell health indexes update-data retrain

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Copied .env.example to .env"; \
		echo "Please edit .env before continuing"; \
	else \
		echo ".env already exists"; \
	fi

dev:
	FLASK_ENV=development python app.py

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f web

shell:
	docker compose exec web bash

health:
	curl -s localhost:8000/health | python -m json.tool

indexes:
	python scripts/create_indexes.py

update-data:
	python scripts/update_mandi_data.py --source file --path $(PATH)

retrain:
	python ml/data_pipeline.py && python ml/train_model.py --retrain
