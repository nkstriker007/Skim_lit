import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import User, Prediction, RequestLog
from schemas import UserCreate, LabelCount, AnalyticsOut
from utils import hash_password


# ─── Users ───────────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ─── Predictions ─────────────────────────────────────────────────────────────

def save_prediction(db: Session, user_id: int, abstract: str, results: list):
    pred = Prediction(
        user_id=user_id,
        abstract=abstract,
        results=json.dumps([r.dict() for r in results])
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def get_user_history(db: Session, user_id: int):
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(Prediction.created_at.desc())
        .limit(50)
        .all()
    )


# ─── Logging ─────────────────────────────────────────────────────────────────

def log_request(db: Session, user_id: int, endpoint: str):
    log = RequestLog(user_id=user_id, endpoint=endpoint)
    db.add(log)
    db.commit()


# ─── Analytics ───────────────────────────────────────────────────────────────

def get_analytics(db: Session, user_id: int) -> AnalyticsOut:
    predictions = get_user_history(db, user_id)

    total_predictions = len(predictions)
    label_counts: dict[str, int] = {}
    total_sentences = 0

    for pred in predictions:
        results = json.loads(pred.results)
        total_sentences += len(results)
        for r in results:
            label = r["label"]
            label_counts[label] = label_counts.get(label, 0) + 1

    since = datetime.utcnow() - timedelta(days=7)
    requests_last_7 = (
        db.query(RequestLog)
        .filter(RequestLog.user_id == user_id, RequestLog.created_at >= since)
        .count()
    )

    label_distribution = [
        LabelCount(label=label, count=count)
        for label, count in sorted(label_counts.items(), key=lambda x: -x[1])
    ]

    return AnalyticsOut(
        total_predictions=total_predictions,
        total_sentences_classified=total_sentences,
        label_distribution=label_distribution,
        requests_last_7_days=requests_last_7
    )
