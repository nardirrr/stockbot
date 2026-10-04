import os
import sys
import requests
import yfinance as yf

# ==========================================
# 1. PORTFOLIO CONFIGURATION
# ==========================================
# This dictionary maps Yahoo Finance ticker symbols to the names you want to see in Telegram.
# This is an EXAMPLE portfolio of holdings. **PLEASE EDIT ACCORDINGLY**
PORTFOLIO = {
    'VWRP.L': 'Vanguard All-World ETF',
    'VALL.L': 'Vanguard Global All-Cap',
    'SGLN.L': 'Physical Gold ETC',
    'AAPL': 'Apple Inc.'
}

def fetch_market_data() -> str:
    """
    Queries Yahoo Finance for the latest closing prices and formats them into a Markdown string.
    """
    lines = ["🌅 **Pre-Market Briefing**\n"]
    
    for symbol, name in PORTFOLIO.items():
        try:
            ticker = yf.Ticker(symbol)
            
            # Fetch 5 days to ensure data is returned after weekends or public holidays
            hist = ticker.history(period="5d")
            
            if hist.empty:
                lines.append(f"• *{name}*: Data unavailable")
                continue
                
            latest_close = hist['Close'].iloc[-1]
            
            # Determine actual currency denomination from Yahoo Finance metadata
            try:
                currency = ticker.fast_info.currency
            except Exception:
                currency = 'GBP' if symbol.endswith('.L') else 'USD'
            
            # --- DYNAMIC CURRENCY FORMATTING ---
            if currency in ['GBp', 'GBX']:
                # Pence Sterling (GBX) converted to Pounds
                lines.append(f"• *{name}*: £{latest_close / 100:.2f}")
            elif currency == 'GBP':
                lines.append(f"• *{name}*: £{latest_close:.2f}")
            elif currency == 'EUR':
                lines.append(f"• *{name}*: €{latest_close:.2f}")
            else:
                lines.append(f"• *{name}*: ${latest_close:.2f}")
                
        except Exception:
            lines.append(f"• *{name}*: Error fetching data")
            
    return "\n".join(lines)

def send_telegram_message(message: str) -> None:
    """
    Pushes the formatted text payload to the Telegram Bot API.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Error: Telegram credentials not found in environment variables.")
        sys.exit(1)
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id.strip(),
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        # Log response body if Telegram rejects the request
        if not response.ok:
            print(f"Telegram API Error: {response.text}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    report = fetch_market_data()
    send_telegram_message(report)
    print("Report dispatched successfully.")
