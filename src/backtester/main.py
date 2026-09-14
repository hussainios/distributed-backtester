from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from backtester.config import get_settings
from backtester.database import Base, engine, get_session
from backtester.engine import run_backtest
from backtester.models import BacktestJob
from backtester.schemas import BacktestRequest, BacktestResponse

settings = get_settings()

app = FastAPI(
    title="Distributed Backtester",
    description="An incremental distributed backtesting system.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.post("/backtests", response_model=BacktestResponse, status_code=201, tags=["backtests"])
def create_backtest(
    request: BacktestRequest, session: Session = Depends(get_session)
) -> BacktestJob:
    job = BacktestJob(
        id=uuid4(),
        strategy=request.strategy,
        parameters=request.parameters,
        instrument=request.instrument,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_capital=request.initial_capital,
        commission_bps=request.commission_bps,
        slippage_bps=request.slippage_bps,
        status="running",
    )
    session.add(job)
    session.commit()

    try:
        job.result = run_backtest(
            strategy=job.strategy,
            parameters=job.parameters,
            instrument=job.instrument,
            start_date=job.start_date,
            end_date=job.end_date,
            initial_capital=job.initial_capital,
            commission_bps=job.commission_bps,
            slippage_bps=job.slippage_bps,
        )
        job.status = "completed"
        job.completed_at = datetime.now(UTC)
    except ValueError as error:
        job.status = "failed"
        job.error = str(error)
    session.commit()
    return job


@app.get("/backtests/{job_id}", response_model=BacktestResponse, tags=["backtests"])
def get_backtest(
    job_id: UUID, session: Session = Depends(get_session)
) -> BacktestJob:
    job = session.get(BacktestJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="backtest not found")
    return job
