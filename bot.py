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

# تنبيه تشغيل السيرفر
send_telegram_message("📡 تم تشغيل الرادار التلقائي لـ SPX500 على سيرفر Render بنجاح! السيرفر شغال الآن 24/7 بالخلفية وسيصيد لك الفرص تلقائياً.")

last_alert_type = None  

while True:
    try:
        data_15m = yf.download(tickers="^SPX", period="5d", interval="15m", progress=False)
        recent_15m = data_15m.tail(24)
        highest_high = float(recent_15m['High'].max().iloc[0] if isinstance(recent_15m['High'].max(), pd.Series) else recent_15m['High'].max())
        lowest_low = float(recent_15m['Low'].min().iloc[0] if isinstance(recent_15m['Low'].min(), pd.Series) else recent_15m['Low'].min())
        equilibrium_50 = (highest_high + lowest_low) / 2
        
        ob_zone_low = lowest_low
        ob_zone_high = lowest_low + (highest_high - lowest_low) * 0.15

        data_1m = yf.download(tickers="^SPX", period="1d", interval="1m", progress=False)
        current_price = float(data_1m['Close'].iloc[-1].iloc[0] if isinstance(data_1m['Close'].iloc[-1], pd.Series) else data_1m['Close'].iloc[-1])
        
        c1_high_1m = float(data_1m['High'].iloc[-3].iloc[0] if isinstance(data_1m['High'].iloc[-3], pd.Series) else data_1m['High'].iloc[-3])
        c3_low_1m = float(data_1m['Low'].iloc[-1].iloc[0] if isinstance(data_1m['Low'].iloc[-1], pd.Series) else data_1m['Low'].iloc[-1])
        c2_close_1m = float(data_1m['Close'].iloc[-2].iloc[0] if isinstance(data_1m['Close'].iloc[-2], pd.Series) else data_1m['Close'].iloc[-2])
        c2_open_1m = float(data_1m['Open'].iloc[-2].iloc[0] if isinstance(data_1m['Open'].iloc[-2], pd.Series) else data_1m['Open'].iloc[-2])
        fvg_on_1m = (c3_low_1m > c1_high_1m) and (c2_close_1m > c2_open_1m)

        if current_price < equilibrium_50:  
            if ob_zone_low <= current_price <= ob_zone_high:
                if last_alert_type != "OB_ENTRY":
                    msg = f"🔥 إشارة دخول دقيقة (CALL):\nالسعر يلامس الآن الـ Order Block على فريم 15m!\n\n🔹 السعر الحالي: {current_price:.2f}\n🛑 وقف الخسارة: إغلاق تحت {ob_zone_low:.2f}\n💰 الهدف: {equilibrium_50:.2f}"
                    send_telegram_message(msg)
                    last_alert_type = "OB_ENTRY"
            elif fvg_on_1m:
                if last_alert_type != "FVG_ENTRY":
                    msg = f"⚡️ تنبيه دخول سريع (CALL):\nتشكلت فجوة سعرية صاعدة (Bullish FVG) على فريم الدقيقة داخل الـ Discount!\n\n🔹 السعر الحالي: {current_price:.2f}\n🛑 وقف الخسارة: قاع الشمعة السابقة\n💰 الهدف: {highest_high:.2f}"
                    send_telegram_message(msg)
                    last_alert_type = "FVG_ENTRY"
            else:
                last_alert_type = None
        else:
            last_alert_type = "PREMIUM_ZONE"

    except Exception as e:
        pass
    
    time.sleep(60)
