from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .models import SessionLocal, Trace

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/metrics/traces")
def get_traces(limit: int = 10, db: Session = Depends(get_db)):
    traces = db.query(Trace).order_by(Trace.id.desc()).limit(limit).all()
    return [{
        "id": t.id,
        "session_id": t.session_id,
        "message": t.user_message,
        "intent": t.nlu_intent,
        "action": t.plan_action,
        "latency": f"{t.latency_ms}ms",
        "model": t.model_name,
        "time": t.created_at.strftime("%H:%M:%S")
    } for t in traces]