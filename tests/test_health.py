from fastapi.testclient import TestClient

from backtester.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_backtest() -> None:
    response = client.post(
        "/backtests",
        json={
            "strategy": "moving_average_crossover",
            "parameters": {"fast_window": 5, "slow_window": 20},
            "instrument": "SPY",
            "start_date": "2020-01-01",
            "end_date": "2021-01-01",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "completed"
    assert body["result"]["data_points"] > 0
