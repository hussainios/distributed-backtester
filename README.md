# Distributed Backtester

An incremental project for learning production engineering by building a distributed backtesting system.

The first milestone is intentionally small: a typed FastAPI service that accepts a strategy and date range, runs a deterministic backtest, and persists the job and result. The queue, workers, retries, observability, and AWS deployment will be added as separate milestones so each design decision stays understandable.

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

Run a backtest against the current deterministic demo data:

```bash
curl -X POST http://localhost:8000/backtests \
  -H 'Content-Type: application/json' \
  -d '{
    "strategy": "moving_average_crossover",
    "parameters": {"fast_window": 20, "slow_window": 50},
    "instrument": "SPY",
    "start_date": "2020-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 100000,
    "commission_bps": 1,
    "slippage_bps": 2
  }'
```

The demo data provider is deliberately deterministic and is not real market data. Replacing it with CSV/S3 market data is the next data-engineering milestone.

## Checks

```bash
pytest
ruff check .
mypy src
```

## Planned milestones

1. Replace demo prices with validated historical market data.
2. Add a local durable queue.
3. Run multiple workers with retries and idempotency.
4. Add metrics, structured logs, and failure simulation.
5. Benchmark scaling locally before choosing AWS services.
