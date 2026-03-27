from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db, engine
from models import Base
from schemas import (
    UserCreate, UserOut, Token,
    PredictRequest, PredictResponse,
    HistoryOut, AnalyticsOut
)
import auth, crud, inference
import traceback
from fastapi import HTTPException

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkimLit API",
    description="Biomedical abstract sentence classifier — NLP backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once on startup
@app.on_event("startup")
async def startup_event():
    inference.load_models()

# ─── Auth ────────────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@app.post("/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ─── Predict ─────────────────────────────────────────────────────────────────
"""
@app.post("/predict", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    results = inference.classify_abstract(request.abstract)
    crud.save_prediction(db, user_id=current_user.id,
                         abstract=request.abstract, results=results)
    crud.log_request(db, user_id=current_user.id, endpoint="/predict")
    return {"sentences": results}
"""
@app.post("/predict", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    try:
        results = inference.classify_abstract(request.abstract)
        crud.save_prediction(db, user_id=current_user.id,
                             abstract=request.abstract, results=results)
        crud.log_request(db, user_id=current_user.id, endpoint="/predict")
        return {"sentences": results}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── History ─────────────────────────────────────────────────────────────────

@app.get("/history", response_model=list[HistoryOut])
def get_history(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    return crud.get_user_history(db, user_id=current_user.id)


# ─── Analytics ───────────────────────────────────────────────────────────────

@app.get("/analytics/usage", response_model=AnalyticsOut)
def get_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    return crud.get_analytics(db, user_id=current_user.id)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": inference.model_loaded()}
