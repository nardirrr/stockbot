# Financial Market Briefing Telegram Bot

An automated Python service that aggregates financial market movements, calculates key metrics, and delivers structured daily intelligence briefings straight to Telegram via the Telegram Bot API. This bot uses the Github YAML language to automate and schedule it's run, which then gets passed to telegram

**Why I Did This**

I manage my investments actively, but checking individual positions during a busy morning routine requires deliberate manual interaction. Built-in OS widgets (like Pixel's At a Glance) generally summarise market movements after the market closes, rather than delivering proactive morning intelligence before the trading day begins.

I wanted an automated, zero-friction delivery system that:
- **Pushes directly to my devices:** Dispatches an early morning notification straight to Telegram with zero manual app switching.
- **Provides contextual direction at a glance:** Clearly highlights whether key indices, equities, and commodities are trending up or down before the morning commute, before markets open.
- **Summarises the underlying movement:** Delivers a concise data breakdown explaining **why** the movement occurred, allowing me to digest market conditions in 30 seconds while on the go.

## Core Capabilities
- **Automated Market Polling:** Queries market data and equity metrics utilising `yfinance`.
- **Data Transformation:** Cleans and formats raw time-series data using `pandas`.
- **Scheduled Telegram Delivery:** Builds structured markdown alerts and pushes them directly to private chats or channels via the Telegram Bot API (`requests`).
- **Secure Environment Management:** Isolates configuration, sensitive tokens, and chat IDs via `.env` environment variables.

## Tech Stack
- **Language:** Python 3
- **Libraries:** `requests`, `pandas`, `yfinance`, `python-dotenv`
- **APIs:** Telegram Bot API, Yahoo Finance API

## Architecture & How It Works
1. **Extraction:** The script queries asset symbols (indices, equities, or commodities) via Yahoo Finance endpoints.
2. **Processing:** `pandas` calculates daily percentage changes and formats clean numerical outputs.
3. **Dispatch:** The payload is assembled into formatted Markdown and transmitted via an HTTPS POST request to Telegram's `sendMessage` endpoint.

## Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/telegram-market-bot.git](https://github.com/your-username/telegram-market-bot.git)
   cd telegram-market-bot

2. **Edit the Python Script**
     Using a code editor (notepad/ Google Antigravity / VS code) , edit the python script with the ticker symbols of your choice, to create your own "portfolio"
   
4. **Save the Python File before confirming**
