
# **AI Stock Trader**

## **Table of Contents**
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Adding Symbols and Exchanges](#adding-symbols-and-exchanges)
- [Project Structure](#project-structure)

---

## **Introduction**

Welcome to **AI Stock Trader**, a powerful tool designed to fetch real-time stock market data, calculate key technical indicators using AI-powered strategies, and generate trading signals. This project enables continuous data analysis and backtesting, making it an essential tool for modern traders.

---

## **Features**

- **AI-Powered Trading Strategies:** Implement customizable AI-driven trading strategies.
- **Real-Time Data Fetching:** Fetch OHLCV data from TradingView at regular intervals.
- **Technical Indicator Calculation:** Automatically compute RSI, MACD, and StochRSI indicators.
- **Signal Generation:** Generate buy and sell signals based on defined AI strategies.
- **Robust Error Handling:** Gracefully handle data fetch errors and retries.

---

## **Installation**

### **Prerequisites**

- Python 3.7 or higher
- `pip` package manager
- TradingView account (optional but recommended for full data access)

### **Clone the Repository**

```bash
git clone https://github.com/yourusername/ai-stock-trader.git
cd ai-stock-trader
```

### **Install Required Packages**

```bash
pip install -r requirements.txt
```

### **Setup Configuration**

Edit the `config/strategy_config.json` file to customize your AI-driven trading strategy parameters.

---

## **Usage**

### **Starting the Data Fetcher**

Run the data fetcher to continuously update your data and generate signals:

```python
from data_fetcher import start_data_fetching

start_data_fetching(chart, 'data/ohlcv.csv', 'data/signals.csv', 'BTCUSD', 'Binance', 'config/strategy_config.json')
```

---

## **Configuration**

### **Strategy Configuration**
The `config/strategy_config.json` file allows you to define the parameters for your AI trading strategy, including:

- **Take Profit**: Percentage at which to take profit.
- **Stop Loss**: Percentage at which to stop loss.
- **RSI Period**: Number of periods for RSI calculation.
- **MACD Parameters**: Fast, slow, and signal periods for MACD calculation.
- **StochRSI Period**: Period for StochRSI calculation.
- **Overbought/Oversold Levels**: Thresholds for RSI and StochRSI.

---

## **Adding Symbols and Exchanges**

You can add symbols and exchanges to track by editing the `config/targets.csv` file. This allows you to customize the stocks or other financial instruments you want to monitor.

### **Symbol and Exchange List**

A comprehensive list of symbols and exchanges can be found at [TradingView Database](https://tvdb.brianthe.dev/). Use this resource to find the correct identifiers for the symbols and exchanges you wish to track.

---

## **Project Structure**

```plaintext
├── data_fetcher.py           # Main script for fetching and updating data
├── trading_strategy.py       # Handles indicator calculations and signal generation
├── indicators/               # Custom indicator implementations (RSI, MACD, StochRSI)
├── utils/                    # Utility functions (file handling, signal processing)
├── data/                     # Directory for storing OHLCV and signal data
├── config/                   # Configuration files (strategy_config.json, targets.csv)
├── requirements.txt          # Required Python packages
└── README.md                 # Project documentation
```

