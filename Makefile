.PHONY: configure pull up logs smoke test down clean-data

configure:
	cp -n .env.example .env || true

pull:
	docker compose exec ollama ollama pull "$${OLLAMA_MODEL:-gemma3:1b}"

up:
	docker compose up -d --build

logs:
	docker compose logs -f api

smoke:
	python3 scripts/smoke_test.py

test:
	pytest -q

down:
	docker compose down

clean-data:
	docker compose down --volumes

