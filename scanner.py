import os
import sys
import requests
import yfinance as yf

# ==========================================
# 1. PORTFOLIO CONFIGURATION
# ==========================================
# This dictionary maps Yahoo Finance ticker symbols to the names you want to see in Telegram.
# The '.L' suffix denotes assets listed on the London Stock Exchange.
# This is an EXAMPLE portfolio of holdings that some people might own. **PLEASE EDIT ACCORDINGLY**
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
    # We build the message as a list of strings, which we will join together at the end.
    lines = ["🌅 **Pre-Market Briefing**\n"]
    
    for symbol, name in PORTFOLIO.items():
        try:
            # yf.Ticker creates an object representing the asset.
            ticker = yf.Ticker(symbol)
            
            # Why 5 days? Markets close on weekends and bank holidays. 
            # If we only ask for "1d" on a Monday morning, the API might return empty data.
            # Requesting 5 days guarantees we catch the most recent valid trading close.
            hist = ticker.history(period="5d")
            
            if hist.empty:
                lines.append(f"• *{name}*: Data unavailable")
                continue
                
            # .iloc[-1] targets the last row in the pandas DataFrame (the most recent day).
            # We specifically extract the 'Close' column value.
            latest_close = hist['Close'].iloc[-1]
            
            # --- CURRENCY NORMALISATION LOGIC ---
            # UK-listed assets (like VWRP or SGLN) are often quoted in Pence Sterling (GBX), not Pounds (GBP).
            if symbol.endswith('.L'):
                # If the price is over 1000 pence (e.g., £10.00), we divide by 100 to convert to GBP.
                # This prevents your bot from telling you an ETF costs £12,000 instead of £120.00.
                if latest_close > 1000:
                    lines.append(f"• *{name}*: £{latest_close/100:.2f}")
                else:
                    lines.append(f"• *{name}*: £{latest_close:.2f}")
            else:
                # US equities (like AAPL) default to USD.
                lines.append(f"• *{name}*: ${latest_close:.2f}")
                
        except Exception as e:
            # If an individual ticker fails (e.g., Yahoo Finance API goes down), 
            # the bot gracefully skips it rather than crashing the whole script.
            lines.append(f"• *{name}*: Error fetching data")
            
    # Combines the list into a single string, with each item on a new line.
    return "\n".join(lines)

def send_telegram_message(message: str) -> None:
    """
    Pushes the formatted text payload to the Telegram Bot API.
    """
    # os.getenv pulls your secure keys from the system environment.
    # We never hardcode these in the file so they don't leak on GitHub.
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Defensive programming: Stop immediately if the keys are missing.
    if not bot_token or not chat_id:
        print("Error: Telegram credentials not found in environment variables.")
        sys.exit(1) # Exit code 1 tells the operating system/GitHub Actions that the script failed.
        
    # The official Telegram API endpoint for sending text messages.
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # The payload dictates where the message goes and how it looks.
    # parse_mode="Markdown" allows the use of asterisks (*) for bold text in the report.
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        # We send an HTTPS POST request. A timeout of 10 seconds prevents the script 
        # from hanging forever if Telegram's servers are slow.
        response = requests.post(url, json=payload, timeout=10)
        
        # raise_for_status() throws an error if Telegram rejects the message (e.g., wrong chat ID).
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send message: {e}")
        sys.exit(1)

# This block ensures the code only runs if the file is executed directly 
# (e.g., `python bot.py`), rather than if it gets imported into another project.
if __name__ == "__main__":
    report = fetch_market_data()
    send_telegram_message(report)
    print("Report dispatched successfully.")
