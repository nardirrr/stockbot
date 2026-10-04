# Financial Market Briefing Telegram Bot

An automated Python service that aggregates financial market movements, calculates key metrics, and delivers structured daily intelligence briefings straight to Telegram via the Telegram Bot API. This bot uses the Github YAML language to automate and schedule it's run, which then gets passed to telegram.

**Why I Did This**

I manage my investments actively, but checking individual positions during a busy morning routine requires deliberate manual interaction. Built-in OS widgets (like Pixel's At a Glance) generally summarise market movements after the market closes, rather than delivering proactive morning intelligence before the trading day begins.

I wanted an automated, zero-friction delivery system that:
- **Pushes directly to my devices:** Dispatches an early morning notification straight to Telegram with zero manual app switching. Due to Telegrams notification system, this message can be reflected onto an appropriate smartwatch /  pair of earbuds.

- **Provides contextual direction at a glance:** Clearly highlights key indices, equities, and commodities prices before the morning commute, before markets open.

## Future Plans

**Trend calculations coming in the future**

- **Summarise the underlying movement:** Delivers a concise data breakdown explaining **why** the movement occurred, allowing me to digest market conditions in 30 seconds while on the go.

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
1. **Extraction:** The script queries asset symbols (indices, equities, or commodities) via Yahoo Finance endpoints. **Trigger** A GitHub Actions cron workflow spins up an isolated Ubuntu container Monday through Friday at 06:45 UTC (07:45 BST).
2.**Extraction:** `bot.py` queries asset symbols via Yahoo Finance endpoints, requesting a 5-day rolling window to guarantee closing data over weekends and bank holidays. **Processing:** `pandas` calculates daily percentage changes and formats clean numerical outputs. The script inspects currency metadata, converts pence quotes into pounds where applicable, and formats values into clean Markdown text
3. **Dispatch:** The payload is assembled into formatted Markdown and transmitted via an HTTPS POST request to Telegram's `sendMessage` endpoint.

## Setup & Deployment Guide 
This project is built to run 100% in the cloud. You do not need to install Python, configure local virtual environments, or leave your computer powered on.

## Step 1: 
Fork the Repository Click the **Fork** button in the top-right corner of this repository (above **Insights** and **About** )to generate an identical copy under your personal GitHub profile. 

## Step 2: Customise Your Portfolio
 1. In your forked repository, open `bot.py`. 

2. Click the pencil icon to edit the file directly in your browser. 

3. Update the `PORTFOLIO` dictionary at the top with your desired ticker symbols from Yahoo Finance:

**Example Portfolio Provided**

" ```python PORTFOLIO = { 'VWRP.L': 'Vanguard All-World ETF', 'VALL.L': 'Vanguard Global All-Cap', 'SGLN.L': 'Physical Gold ETC', 'AAPL': 'Apple Inc.' } "


4. Commit / Save changes.

## Add Github Secrets ( Telegram info)

Message @botfather on telegram to **create a bot** and get your **api token** (Botfather will provide instructions)
Retrieve the bots username / ID and message it “/start” to initiate it.
Message @userinfobot “/start” to retrieve your numeric id .
Once you fork the repository, open it, navigate to **settings** > **Secrets and variables** > **Actions**.
Click New repository secret and create the following two secrets:
TELEGRAM_BOT_TOKEN: Your API token from BotFather. (Case Sensitive)

TELEGRAM_CHAT_ID: Your numeric Telegram chat ID. (Case Sensitive)

 ## Enable Workflow & Test
Click the Actions tab at the top of your repository.

Click the green button labelled "I understand my workflows, go ahead and enable them" (GitHub pauses automated cron workflows on newly forked repositories by default).

Select Pre-Market Telegram Briefing in the left sidebar.

Click Run workflow > Run workflow to perform an on-demand test run. Check your Telegram chat to verify that the briefing arrives. **It could take a minute**


