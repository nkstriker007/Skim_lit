# 🔬 Biomedical Abstract Classifier

Automatically classifies sentences in biomedical research abstracts into their rhetorical roles: **Background, Objective, Methods, Results, and Conclusions**.

Built on the [PubMed 200k RCT dataset](https://github.com/Franck-Dernoncourt/pubmed-rct).

---

## Architecture

```
┌─────────────────────┐       REST API        ┌──────────────────────┐
│   Streamlit Frontend │ ──── /predict ──────▶ │   FastAPI Backend     │
│   (port 8501)        │ ◀─── JSON results ─── │   (port 8000)         │
└─────────────────────┘                        └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │   TensorFlow Model    │
                                               │   (Model 5 — token +  │
                                               │   char + positional)  │
                                               └──────────────────────┘
```

## Model Results

| Model | Accuracy | F1 | Architecture |
|---|---|---|---|
| Baseline (TF-IDF) | 72.2% | 0.699 | Multinomial NB |
| Model 1 | 77.7% | 0.775 | Conv1D + token embeddings |
| Model 5 (deployed) | 88.9% | 0.89 | Token + Char + Positional (multimodal) |
| PubMedBERT (benchmark) | ~90%+ | ~0.89+ | Fine-tuned transformer |

> Model 5 is the deployed model. PubMedBERT serves as a state-of-the-art benchmark.

---

## Features

- **Abstract classification** — sentence-level label prediction with confidence scores
- **JWT authentication** — register and login to use the API
- **History** — every classification is saved and viewable
- **Analytics** — usage stats and label distribution per user
- **REST API** — fully documented at `/docs` (FastAPI auto-docs)

---

## Quick Start (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/skimlit-app
cd skimlit-app

# 2. Add your trained model
mkdir saved_models
# copy skimlit_model5_best/ and class_names.json into saved_models/

# 3. Run everything
docker-compose up --build

# Frontend → http://localhost:8501
# API docs → http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | ❌ | Create account |
| POST | `/auth/login` | ❌ | Get JWT token |
| POST | `/predict` | ✅ | Classify abstract |
| GET | `/history` | ✅ | Past classifications |
| GET | `/analytics/usage` | ✅ | Usage stats |
| GET | `/health` | ❌ | Health check |

Full interactive docs: `http://localhost:8000/docs`

---

## Stack

- **Backend** — FastAPI, SQLAlchemy, JWT (python-jose), bcrypt
- **ML** — TensorFlow / Keras, Universal Sentence Encoder
- **Frontend** — Streamlit
- **Database** — SQLite (local) / PostgreSQL (production)
- **Deploy** — Docker Compose → Render
