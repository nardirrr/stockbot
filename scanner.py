import os
import requests
import pandas as pd
import yfinance as yf

# Pull credentials securely from the GitHub vault
TELEGRAM_BOT_TOKEN = os.environ.get('8742193604:AAFOFUr5qBgJYj-q9OpaqOcLxum0sk0TLA0')
TELEGRAM_CHAT_ID = os.environ.get('8334826606')

CUSTOM_TICKERS = ['SNAP', 'TSM', '005930.KS', 'AAPL']

def send_telegram_chunked(text):
    """Splits massive messages so Telegram doesn't reject them."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Split the giant list into 4000-character blocks
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    
    for chunk in chunks:
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

def run_instant_price_test():
    try:
        sp500 = [t.replace('.', '-') for t in pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']]
        ftse100 = [f"{t}.L" for t in pd.read_html('https://en.wikipedia.org/wiki/FTSE_100_Index', match='Ticker')[0]['Ticker']]
        ftse250 = [f"{t}.L" for t in pd.read_html('https://en.wikipedia.org/wiki/FTSE_250_Index', match='Ticker')[0]['Ticker']]
        tickers = list(set(sp500 + ftse100 + ftse250 + CUSTOM_TICKERS))
    except:
        tickers = CUSTOM_TICKERS

    # period="1d" grabs the data for today only, making it incredibly fast
    data = yf.download(tickers, period="1d", group_by='ticker', threads=True, progress=False)
    
    price_list = []

    for ticker in tickers:
        try:
            if len(tickers) == 1:
                current_price = data['Close'].iloc[-1]
            else:
                if ticker not in data or 'Close' not in data[ticker]: continue
                # .dropna() ensures we grab the absolute latest valid number
                current_price = data[ticker]['Close'].dropna().iloc[-1]
                
            price_list.append(f"• **{ticker}**: ${current_price:.2f}")
        except:
            continue

    # Sort them alphabetically so you can actually read through them
    price_list.sort()
    
    final_message = "🟢 **LIVE RAW PRICE TEST** 🟢\n\n" + "\n".join(price_list)
    send_telegram_chunked(final_message)

if __name__ == "__main__":
    run_instant_price_test()
