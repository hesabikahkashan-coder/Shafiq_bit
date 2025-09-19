# BTC Short-term Predictor (LSTM)

## Setup (local)
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python train.py
5. uvicorn app:app --reload --port 8000

## Endpoints
- POST /predict
- GET /health
