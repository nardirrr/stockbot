import yfinance as yf
import requests
import pandas as pd
from datetime import datetime
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
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True})

def get_performance(ticker_str):
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
    report.append("📊 **Current Performance**")
    for ticker, name in WATCHLIST_A.items():
        w1, m1, y1, price = get_performance(ticker)
        # Handle LSE pricing (Pence vs Pounds)
        display_price = f"£{price/100:.2f}" if ".L" in ticker else f"${price:.2f}"
        report.append(f"*{name}*: {display_price}\n1W: {w1} | 1M: {m1} | 1Y: {y1}\n")
    
    report.append("\n📰 **Market News Digest**")
    news_links = []
    for t_str in ['GOOGL', 'IBM', 'AAPL', 'MSFT']:
        try:
            stories = yf.Ticker(t_str).news
            for n in stories[:2]:
                title = n.get('title') or n.get('headline')
                link = n.get('link')
                if title and link:
                    news_links.append(f"• [{title}]({link})")
        except: continue
    
    report.append("\n".join(list(set(news_links))[:8]))
    send_msg("\n".join(report))

def check_commands():
    """Checks for /status command"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        data = requests.get(url).json()
        if data.get("result"):
            last_msg = data["result"][-1].get("message", {}).get("text", "")
            if last_msg == "/status":
                send_msg(f"✅ **E14 Bot Online**\nTime: {datetime.now().strftime('%H:%M:%S')}\nMonitoring Watchlist B...")
    except: pass

def run_volatility_sniper():
    check_commands()
    all_tickers = {**WATCHLIST_A, **WATCHLIST_B}
    for ticker, name in all_tickers.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(interval="1m", period="30m")
            if len(hist) < 11: continue
            now, then = hist['Close'].iloc[-1], hist['Close'].iloc[-11]
            change = ((now - then) / then) * 100
            
            if 2.0 <= abs(change) <= 10.0:
                w1, m1, y1, _ = get_performance(ticker)
                send_msg(f"🚨 **FLASH MOVE**\n*{name}* moved {change:+.1f}% in 10 mins!\nContext: 1W: {w1} | 1M: {m1} | 1Y: {y1}")
        except: continue

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode == "morning":
        run_morning_report()
    else:
        run_volatility_sniper()
