# app.py
import os
import uvicorn
import joblib
import numpy as np
from fastapi import FastAPI, WebSocket
from datetime import datetime
from binance.client import Client
from tensorflow.keras.models import load_model
import pandas as pd

API_KEY = "YOUR_BINANCE_API_KEY"
API_SECRET = "YOUR_BINANCE_API_SECRET"
MODEL_DIR = "models"

app = FastAPI()
client = Client(API_KEY, API_SECRET)

# -------------------------
# بارگذاری آخرین مدل
# -------------------------
def latest_model(symbol="BTCUSDT"):
    models = [f for f in os.listdir(MODEL_DIR) if f.startswith(symbol)]
    if not models:
        return None, None
    models.sort()
    model_file = os.path.join(MODEL_DIR, models[-1])
    scaler_file = os.path.join(MODEL_DIR, models[-1].replace("lstm", "scaler").replace(".h5", ".save"))
    model = load_model(model_file)
    scaler = joblib.load(scaler_file)
    return model, scaler

# -------------------------
# دریافت داده‌های جدید
# -------------------------
def fetch_latest_price(symbol="BTCUSDT", limit=50):
    klines = client.get_klines(symbol=symbol, interval="1h", limit=limit)
    df = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df[["close"]]

# -------------------------
# پیش‌بینی
# -------------------------
@app.get("/predict")
def predict(symbol="BTCUSDT"):
    model, scaler = latest_model(symbol)
    if model is None:
        return {"error": "مدل پیدا نشد. ابتدا train.py را اجرا کنید."}
    
    df = fetch_latest_price(symbol)
    seq_len = 50
    data_scaled = scaler.transform(df)
    X = np.array([data_scaled[-seq_len:]])
    pred_scaled = model.predict(X)
    pred = scaler.inverse_transform(pred_scaled)[0][0]
    
    return {"symbol": symbol, "predicted_price": float(pred), "timestamp": str(datetime.now())}

# -------------------------
# WebSocket زنده
# -------------------------
@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    model, scaler = latest_model(symbol)
    if model is None:
        await websocket.send_json({"error": "مدل پیدا نشد."})
        return
    while True:
        df = fetch_latest_price(symbol)
        seq_len = 50
        data_scaled = scaler.transform(df)
        X = np.array([data_scaled[-seq_len:]])
        pred_scaled = model.predict(X)
        pred = scaler.inverse_transform(pred_scaled)[0][0]
        await websocket.send_json({"symbol": symbol, "predicted_price": float(pred), "timestamp": str(datetime.now())})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)