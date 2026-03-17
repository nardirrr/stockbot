import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import sys

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = '8742193604:AAFOFUr5qBgJYj-q9OpaqOcLxum0sk0TLA0' 
TELEGRAM_CHAT_ID = '8334826606'

WATCHLIST_A = {'GOOGL': 'Google', 'VWRP.L': 'All-World', 'SGLN.L': 'Gold', 'SSLN.L': 'Silver'}
WATCHLIST_B = {
    'AAPL': 'Apple', 'MSFT': 'Microsoft', 'NVDA': 'Nvidia', 'AMZN': 'Amazon', 
    'META': 'Meta', 'TSLA': 'Tesla', 'TSM': 'TSMC', '005930.KS': 'Samsung', 
    'BABA': 'Alibaba', 'IBM': 'IBM', 'RACE': 'Ferrari'
}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})

def get_performance(ticker_str):
    """Calculates performance against dynamic past windows (1W, 1M, 1Y)."""
    t = yf.Ticker(ticker_str)
    hist = t.history(period="1y")
    if hist.empty: return "N/A", "N/A", "N/A", 0
    
    curr = hist['Close'].iloc[-1]
    
    def calc_change(past_val):
        change = ((curr - past_val) / past_val) * 100
        return f"{'🟢' if change >= 0 else '🔴'}{change:+.1f}%"

    w1 = calc_change(hist['Close'].iloc[-5]) if len(hist) > 5 else "N/A"
    m1 = calc_change(hist['Close'].iloc[-21]) if len(hist) > 21 else "N/A"
    y1 = calc_change(hist['Close'].iloc[0])
    
    return w1, m1, y1, curr

def run_morning_report():
    report = ["🌅 **MORNING BRIEFING & NEWS**\n"]
    
    # 1. Market Data
    report.append("📊 **Your Holdings**")
    for ticker, name in WATCHLIST_A.items():
        w1, m1, y1, price = get_performance(ticker)
        report.append(f"*{name}* ({ticker}): ${price:.2f}\n1W: {w1} | 1M: {m1} | 1Y: {y1}\n")
    
    # 2. News Digest (Global Finance & Specific Holdings)
    report.append("\n📰 **Market News Digest**")
    news_items = []
    # Check Google and IBM specifically + broad market
    for t_str in ['GOOGL', 'IBM', 'AAPL', 'MSFT']:
        t = yf.Ticker(t_str)
        for n in t.news[:2]: # Top 2 stories per major ticker
            news_items.append(f"• [{n['title']}]({n['link']})")
    
    report.append("\n".join(set(news_items[:8]))) # Limit to top 8 unique stories
    send_msg("\n".join(report))

def run_volatility_sniper():
    """Checks for 2-10% moves within the last 10 minutes."""
    all_tickers = {**WATCHLIST_A, **WATCHLIST_B}
    for ticker, name in all_tickers.items():
        try:
            # Fetch 1-minute data for the last 30 mins
            t = yf.Ticker(ticker)
            hist = t.history(interval="1m", period="30m")
            if len(hist) < 11: continue
            
            now_price = hist['Close'].iloc[-1]
            ten_min_ago = hist['Close'].iloc[-11]
            
            change = ((now_price - ten_min_ago) / ten_min_ago) * 100
            
            if 2.0 <= abs(change) <= 10.0:
                w1, m1, y1, _ = get_performance(ticker)
                msg = (f"🚨 **FLASH MOVE ALERT**\n*{name}* moved {change:+.1f}% in 10 mins!\n\n"
                       f"💰 Current: ${now_price:.2f}\n"
                       f"📅 Context: 1W: {w1} | 1M: {m1} | 1Y: {y1}")
                send_msg(msg)
        except: continue

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode == "morning":
        run_morning_report()
    else:
        run_volatility_sniper()
