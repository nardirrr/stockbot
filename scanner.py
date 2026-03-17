import requests
import pandas as pd
import yfinance as yf
import time
import os

# Put your actual token and ID here (keep the quotes!)
TELEGRAM_BOT_TOKEN = '8742193604:AAFOFUr5qBgJYj-q9OpaqOcLxum0sk0TLA0'
TELEGRAM_CHAT_ID = '8334826606'

CUSTOM_TICKERS = ['SNAP', 'TSM', '005930.KS', 'AAPL']

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"})

def get_pct(current, past):
    if past == 0 or pd.isna(past): return "N/A"
    change = ((current - past) / past) * 100
    icon = "🟢" if change >= 0 else "🔴"
    return f"{icon}{change:+.1f}%"

def run_market_analytics():
    send_telegram_msg("🚀 **Analytics Engine Starting:** Scrapping S&P 500 & FTSE 350...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        html_sp500 = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=headers).text
        sp_df = pd.read_html(html_sp500)[0]
        sp_map = dict(zip([t.replace('.', '-') for t in sp_df['Symbol']], sp_df['Security']))

        html_ftse100 = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index', headers=headers).text
        f1_df = pd.read_html(html_ftse100, match='Ticker')[0]
        f1_map = dict(zip([f"{t}.L" for t in f1_df['Ticker']], f1_df['Company']))

        html_ftse250 = requests.get('https://en.wikipedia.org/wiki/FTSE_250_Index', headers=headers).text
        f2_df = pd.read_html(html_ftse250, match='Ticker')[0]
        f2_map = dict(zip([f"{t}.L" for t in f2_df['Ticker']], f2_df['Company']))

        # Merge all name maps
        name_map = {**sp_map, **f1_map, **f2_map}
        tickers = list(name_map.keys()) + CUSTOM_TICKERS
        send_telegram_msg(f"✅ Loaded {len(tickers)} stocks. Analyzing performance...")
    except Exception as e:
        send_telegram_msg(f"⚠️ Metadata scrape failed: {e}")
        return

    batch_size = 50 # Smaller batches because we are pulling 1 year of data per stock
    report_lines = []
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        # Pull 1y of data for the whole batch
        data = yf.download(batch, period="1y", group_by='ticker', threads=5, progress=False)
        
        for ticker in batch:
            try:
                hist = data[ticker]['Close'].dropna()
                if len(hist) < 2: continue
                
                curr = hist.iloc[-1]
                name = name_map.get(ticker, ticker)
                
                # Calculations
                d1 = get_pct(curr, hist.iloc[-2] if len(hist) > 1 else 0)
                w1 = get_pct(curr, hist.iloc[-5] if len(hist) > 5 else 0)
                m1 = get_pct(curr, hist.iloc[-21] if len(hist) > 21 else 0)
                m3 = get_pct(curr, hist.iloc[-63] if len(hist) > 63 else 0)
                y1 = get_pct(curr, hist.iloc[0])

                line = (f"🏦 *{name}* ({ticker})\n"
                        f"💰 Price: ${curr:.2f}\n"
                        f"1D: {d1} | 1W: {w1} | 1M: {m1}\n"
                        f"3M: {m3} | 1Y: {y1}\n")
                report_lines.append(line)
            except:
                continue
        
        time.sleep(1) # Breath for Yahoo

    report_lines.sort()
    final_report = "📊 **MASTER MARKET DASHBOARD**\n\n" + "\n".join(report_lines)
    send_telegram_msg(final_report)

if __name__ == "__main__":
    run_market_analytics()
