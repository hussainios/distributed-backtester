# Distributed Backtester

An incremental project for learning production engineering by building a distributed backtesting system.

The first milestone is intentionally small: a typed FastAPI service that can be containerised and run locally. The database, queue, workers, retries, observability, and AWS deployment will be added as separate milestones so each design decision stays understandable.

## Requirements

- Python 3.12+
- Docker and Docker Compose

## Local development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
uvicorn backtester.main:app --reload
```

The API is available at `http://localhost:8000`. OpenAPI documentation is available at `/docs`.

## Docker

```bash
docker compose up --build
```

Check the service with:

```bash
curl http://localhost:8000/health
```

## Checks

```bash
pytest
ruff check .
mypy src
```

## Planned milestones

1. Persist backtest jobs and results in PostgreSQL.
2. Add a local durable queue.
3. Run multiple workers with retries and idempotency.
4. Add metrics, structured logs, and failure simulation.
5. Benchmark scaling locally before choosing AWS services.

