import requests
import pandas as pd
import yfinance as yf
import time

# Put your actual token and ID here (keep the quotes!)
TELEGRAM_BOT_TOKEN = '8742193604:AAFOFUr5qBgJYj-q9OpaqOcLxum0sk0TLA0' 
TELEGRAM_CHAT_ID = '8334826606'

CUSTOM_TICKERS = ['SNAP', 'TSM', '005930.KS', 'AAPL']

def send_telegram_msg(text):
    """Splits messages to respect Telegram's 4000-character limit."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"})

def run_full_market_test():
    send_telegram_msg("⏳ **System Active:** Assembling the S&P 500 and FTSE 350...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # 1. Scrape S&P 500
        html_sp500 = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=headers).text
        sp500 = [t.replace('.', '-') for t in pd.read_html(html_sp500)[0]['Symbol']]
        
        # 2. Scrape FTSE 100 and FTSE 250 (The FTSE 350)
        html_ftse100 = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index', headers=headers).text
        ftse100 = [f"{t}.L" for t in pd.read_html(html_ftse100, match='Ticker')[0]['Ticker']]
        
        html_ftse250 = requests.get('https://en.wikipedia.org/wiki/FTSE_250_Index', headers=headers).text
        ftse250 = [f"{t}.L" for t in pd.read_html(html_ftse250, match='Ticker')[0]['Ticker']]
        
        # Combine everything and remove duplicates
        tickers = list(set(sp500 + ftse100 + ftse250 + CUSTOM_TICKERS))
        send_telegram_msg(f"✅ Scraped {len(tickers)} total tickers. Beginning batch downloads...")
        
    except Exception as e:
        tickers = CUSTOM_TICKERS
        send_telegram_msg("⚠️ Scraping failed. Falling back to custom tickers.")

    # --- THE BATCH PROCESSOR ---
    batch_size = 100
    price_list = []
    total_batches = (len(tickers) // batch_size) + 1
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        current_batch_num = (i // batch_size) + 1
        
        # Ping Telegram so you know it hasn't frozen
        send_telegram_msg(f"🔄 Processing batch {current_batch_num} of {total_batches}...")
        
        # Download just this chunk of 100 stocks
        data = yf.download(batch, period="1d", group_by='ticker', threads=5, progress=False)
        
        for ticker in batch:
            try:
                if len(batch) == 1:
                    current_price = data['Close'].iloc[-1]
                else:
                    if ticker not in data or 'Close' not in data[ticker]: continue
                    current_price = data[ticker]['Close'].dropna().iloc[-1]
                    
                price_list.append(f"• **{ticker}**: ${current_price:.2f}")
            except:
                continue
                
        # Pause for 2 seconds so Yahoo Finance doesn't block us
        time.sleep(2)

    # Sort alphabetically and format
    price_list.sort()
    final_message = "🟢 **FULL MARKET RESULTS** 🟢\n\n" + "\n".join(price_list)
    
    send_telegram_msg("✅ All data processed. Sending massive price list now...")
    send_telegram_msg(final_message)

if __name__ == "__main__":
    run_full_market_test()
