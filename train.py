# train.py
import os
import pandas as pd
import numpy as np
from datetime import datetime
from binance.client import Client
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import logging

# -------------------------
# تنظیمات اولیه
# -------------------------
API_KEY = "YOUR_BINANCE_API_KEY"
API_SECRET = "YOUR_BINANCE_API_SECRET"
DATA_DIR = "data"
MODEL_DIR = "models"
LOG_DIR = "logs"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(filename=os.path.join(LOG_DIR, "training.log"),
                    level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s")

# -------------------------
# دریافت داده‌ها
# -------------------------
client = Client(API_KEY, API_SECRET)

def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
    return df[["open_time", "close"]]

# -------------------------
# آماده‌سازی داده‌ها
# -------------------------
def prepare_data(df, seq_len=50):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["close"]])
    X, y = [], []
    for i in range(seq_len, len(scaled)):
        X.append(scaled[i-seq_len:i])
        y.append(scaled[i])
    X, y = np.array(X), np.array(y)
    return X, y, scaler

# -------------------------
# ساخت مدل LSTM ساده
# -------------------------
def build_lstm(input_shape):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# -------------------------
# آموزش مدل
# -------------------------
def train_model(symbol="BTCUSDT"):
    logging.info(f"شروع آموزش مدل برای {symbol}")
    df = fetch_binance_data(symbol)
    X, y, scaler = prepare_data(df)
    
    model = build_lstm(X.shape[1:])
    model.fit(X, y, epochs=10, batch_size=32, verbose=1)
    
    # ذخیره مدل و scaler
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_file = os.path.join(MODEL_DIR, f"{symbol}_lstm_{date_str}.h5")
    scaler_file = os.path.join(MODEL_DIR, f"{symbol}_scaler_{date_str}.save")
    model.save(model_file)
    joblib.dump(scaler, scaler_file)
    
    logging.info(f"مدل ذخیره شد: {model_file}")
    logging.info(f"Scaler ذخیره شد: {scaler_file}")

if __name__ == "__main__":
    train_model("BTCUSDT")