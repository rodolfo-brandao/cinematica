up:
	docker compose -f docker/docker-compose.yml --env-file .env up -d

down:
	docker compose -f docker/docker-compose.yml --env-file .env down

ollama-up:
	brew services start ollama

ollama-down:
	brew services stop ollama

api:
	uv run uvicorn src.api.app:app --reload