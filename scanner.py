import requests
import pandas as pd
import yfinance as yf

# Put your actual token and ID here
TELEGRAM_BOT_TOKEN = ('8742193604:AAFOFUr5qBgJYj-q9OpaqOcLxum0sk0TLA0')
TELEGRAM_CHAT_ID = ('8334826606')

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
    print("Scraping Wikipedia using a disguised browser...")
    
    # This header tricks Wikipedia into thinking we are a normal Chrome browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # 1. Grab the raw HTML first using our disguised header
        html_sp500 = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=headers).text
        html_ftse100 = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index', headers=headers).text
        html_ftse250 = requests.get('https://en.wikipedia.org/wiki/FTSE_250_Index', headers=headers).text
        
        # 2. Let pandas read the HTML we just downloaded
        sp500 = [t.replace('.', '-') for t in pd.read_html(html_sp500)[0]['Symbol']]
        ftse100 = [f"{t}.L" for t in pd.read_html(html_ftse100, match='Ticker')[0]['Ticker']]
        ftse250 = [f"{t}.L" for t in pd.read_html(html_ftse250, match='Ticker')[0]['Ticker']]
        
        tickers = list(set(sp500 + ftse100 + ftse250 + CUSTOM_TICKERS))
        print(f"Success! Scraped {len(tickers)} total tickers.")
        
    except Exception as e:
        print(f"Scraping still failed: {e}")
        tickers = CUSTOM_TICKERS

    print("Downloading live market data...")
    # period="1d" grabs the data for today only
    data = yf.download(tickers, period="1d", group_by='ticker', threads=True, progress=False)
    
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
    final_message = "🟢 **LIVE RAW PRICE TEST** 🟢\n\n" + "\n".join(price_list)
    
    print("Sending massive list to Telegram...")
    send_telegram_chunked(final_message)
    print("Done!")

if __name__ == "__main__":
    run_instant_price_test()
