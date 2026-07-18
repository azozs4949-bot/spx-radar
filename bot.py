from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web).start()
import yfinance as yf
import pandas as pd
import requests
import time
import warnings
warnings.filterwarnings('ignore')

TELEGRAM_TOKEN = "8620051828:AAEW_PEthPikCdkoCOkkjddIdEn9eCyFHmg".strip()
TELEGRAM_CHAT_ID = "1804496408"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try: requests.post(url, json=payload)
    except Exception as e: print(f"Error sending to Telegram: {e}")

last_alert_type = None  

while True:
    try:
        # جلب البيانات
        data_15m = yf.download(tickers="^SPX", period="5d", interval="15m", progress=False)
        # حساب متوسط الحجم (Volume Moving Average 20)
        recent_15m = data_15m.tail(24)
        avg_volume = data_15m['Volume'].tail(20).mean()
        current_volume = float(data_15m['Volume'].iloc[-1].iloc[0])
        
        highest_high = float(recent_15m['High'].max())
        lowest_low = float(recent_15m['Low'].min())
        equilibrium_50 = (highest_high + lowest_low) / 2
        
        # مناطق الـ OB
        ob_zone_low = lowest_low
        ob_zone_high = lowest_low + (highest_high - lowest_low) * 0.15
        premium_ob_low = highest_high - (highest_high - lowest_low) * 0.15

        data_1m = yf.download(tickers="^SPX", period="1d", interval="1m", progress=False)
        current_price = float(data_1m['Close'].iloc[-1])

        # تنبيه السيولة (يتم إرساله دائماً إذا زاد الحجم عن المتوسط)
        if current_volume > (avg_volume * 1.5): # زيادة 50% عن المتوسط
            send_telegram_message(f"🚨 تنبيه سيولة مرتفعة:\nحجم التداول الحالي {current_volume:,.0f} أعلى من المتوسط!")

        # منطق الـ CALL (Discount)
        if current_price < equilibrium_50:  
            if ob_zone_low <= current_price <= ob_zone_high:
                if last_alert_type != "OB_ENTRY_CALL":
                    send_telegram_message(f"🔥 إشارة (CALL): السعر يلامس منطقة الطلب (OB)!")
                    last_alert_type = "OB_ENTRY_CALL"
        
        # منطق الـ PUT (Premium)
        else:
            if premium_ob_low <= current_price <= highest_high:
                if last_alert_type != "OB_ENTRY_PUT":
                    send_telegram_message(f"❄️ إشارة (PUT): السعر يلامس منطقة العرض (OB)!")
                    last_alert_type = "OB_ENTRY_PUT"
            else:
                last_alert_type = None

    except Exception as e:
        pass
    
    time.sleep(60)
