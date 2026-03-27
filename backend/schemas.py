from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ─── Predict ─────────────────────────────────────────────────────────────────

class SentenceResult(BaseModel):
    sentence: str
    label: str
    confidence: float


class PredictRequest(BaseModel):
    abstract: str


class PredictResponse(BaseModel):
    sentences: list[SentenceResult]


# ─── History ─────────────────────────────────────────────────────────────────

class HistoryOut(BaseModel):
    id: int
    abstract: str
    results: str          # JSON string — frontend parses
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Analytics ───────────────────────────────────────────────────────────────

class LabelCount(BaseModel):
    label: str
    count: int


class AnalyticsOut(BaseModel):
    total_predictions: int
    total_sentences_classified: int
    label_distribution: list[LabelCount]
    requests_last_7_days: int
