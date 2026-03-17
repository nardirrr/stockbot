import os
import requests
import pandas as pd
import yfinance as yf

# ==========================================
# 1. SECURE CREDENTIALS
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get('8742193604:AAFOFUr5qBgJYj-q9OpaqOcLxum0sk0TLA0')
TELEGRAM_CHAT_ID = os.environ.get('8334826606')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERROR: Could not find Telegram credentials in environment variables.")
    exit()

CUSTOM_TICKERS = ['SNAP', 'TSM', '005930.KS', 'AAPL']

def send_telegram_message(text):
    """Sends messages, chunking them if they exceed Telegram's character limits."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Telegram max length is 4096. We'll split safely at 4000.
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    
    for chunk in chunks:
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ Failed to send a chunk: {response.text}")

def run_raw_price_test():
    send_telegram_message("🟢 **Test Initiated:** Pulling all raw prices now...")
    
    # 1. PULL ALL TICKERS
    print("Scraping index tickers...")
    try:
        sp500 = [t.replace('.', '-') for t in pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']]
        ftse100 = [f"{t}.L" for t in pd.read_html('https://en.wikipedia.org/wiki/FTSE_100_Index', match='Ticker')[0]['Ticker']]
        ftse250 = [f"{t}.L" for t in pd.read_html('https://en.wikipedia.org/wiki/FTSE_250_Index', match='Ticker')[0]['Ticker']]
        tickers = list(set(sp500 + ftse100 + ftse250 + CUSTOM_TICKERS))
        print(f"Loaded {len(tickers)} total tickers.")
    except Exception as e:
        print(f"Scraping failed: {e}. Falling back to custom list.")
        tickers = CUSTOM_TICKERS

    # 2. DOWNLOAD ONLY TODAY'S DATA (Much faster for a raw test)
    print("Downloading current prices...")
    data = yf.download(tickers, period="1d", group_by='ticker', threads=True, progress=False)
    
    price_list = []

    # 3. EXTRACT THE RAW PRICES
    for ticker in tickers:
        try:
            # Handle how yfinance formats single vs multiple ticker downloads
            if len(tickers) == 1:
                current_price = data['Close'].iloc[-1]
            else:
                if ticker not in data or 'Close' not in data[ticker]:
                    continue
                # Grab the very last valid price
                current_price = data[ticker]['Close'].dropna().iloc[-1]
            
            price_list.append(f"• **{ticker}**: ${current_price:.2f}")
                
        except Exception:
            # Skip cleanly if a stock was delisted or has no data today
            continue

    # 4. SEND TO TELEGRAM
    print("Sending massive list to Telegram...")
    
    # Sort them alphabetically to make it easier to read on your phone
    price_list.sort()
    
    final_message = "📊 **RAW STOCK PRICES**\n\n" + "\n".join(price_list)
    send_telegram_message(final_message)
    print("Done! Check your chat.")

if __name__ == "__main__":
    run_raw_price_test()