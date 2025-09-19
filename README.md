# Crypto Predictor

یک پلتفرم حرفه‌ای پیش‌بینی قیمت ارز دیجیتال (BTC, ETH و غیره) با مدل‌های LSTM و قابلیت پیش‌بینی زنده.

## ساختار پروژه
- `train.py` → آموزش مدل‌ها
- `app.py` → API و WebSocket پیش‌بینی
- `models/` → مدل‌های ذخیره شده
- `data/` → داده‌های تاریخی
- `logs/` → لاگ آموزش
- `requirements.txt` → کتابخانه‌های مورد نیاز
- `Dockerfile` → اجرای کانتینری
- `Procfile` → برای deploy روی Heroku / Render

## نصب و اجرای پروژه

1. نصب کتابخانه‌ها:
```bash
pip install -r requirements.txt