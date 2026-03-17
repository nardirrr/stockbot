import requests
import pandas as pd
import yfinance as yf

# Put your actual token and ID here (keep the quotes!)
TELEGRAM_BOT_TOKEN = '8742193604:AAFOFUr5qBgJYj-q9OpaqOcLxum0sk0TLA0'
TELEGRAM_CHAT_ID = '8334826606'

CUSTOM_TICKERS = ['SNAP', 'TSM', '005930.KS', 'AAPL']

def send_telegram_chunked(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"})

def run_lightning_test():
    # 1. Instant Ping
    send_telegram_chunked("⏳ **System Active:** Scraping Wikipedia for FTSE 100...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        html_ftse100 = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index', headers=headers).text
        ftse100 = [f"{t}.L" for t in pd.read_html(html_ftse100, match='Ticker')[0]['Ticker']]
        tickers = list(set(ftse100 + CUSTOM_TICKERS))
        # 2. Progress Ping
        send_telegram_chunked(f"✅ Scraped {len(tickers)} tickers. Downloading market data from Yahoo...")
    except Exception as e:
        tickers = CUSTOM_TICKERS
        send_telegram_chunked(f"⚠️ Scraping failed. Falling back to {len(tickers)} custom tickers.")

    # 3. Controlled Download (limiting threads so Yahoo doesn't block us)
    data = yf.download(tickers, period="1d", group_by='ticker', threads=10, progress=False)
    
    price_list = []

    for ticker in tickers:
        try:
            if len(tickers) == 1:
                current_price = data['Close'].iloc[-1]
            else:
                if ticker not in data or 'Close' not in data[ticker]: continue
                current_price = data[ticker]['Close'].dropna().iloc[-1]
                
            price_list.append(f"• **{ticker}**: ${current_price:.2f}")
        except:
            continue

    price_list.sort()
    final_message = "🟢 **LIVE PRICE RESULTS** 🟢\n\n" + "\n".join(price_list)
    
    # 4. Final Delivery
    send_telegram_chunked(final_message)

if __name__ == "__main__":
    run_lightning_test()
