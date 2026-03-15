up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	pytest -q

lint:
	ruff check .

format:
	ruff check . --fix

migrate:
	alembic upgrade head

ingest-demo:
	curl -X POST http://localhost:8000/api/v1/documents/ingest -F "file=@examples/policies/policy_kyc_1.pdf"

rebuild-index:
	curl -X POST http://localhost:8000/api/v1/index/rebuild

seed-demo:
	@echo "Use ingest-demo multiple times with files in examples/policies"

query-demo:
	curl -X POST http://localhost:8000/api/v1/query -H 'Content-Type: application/json' -d '{"question":"ما متطلبات التحقق من الهوية؟"}'

clean:
	rm -rf .pytest_cache artifacts/uploads/* artifacts/indexes/*
