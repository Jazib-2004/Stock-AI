import time
import logging
import pandas as pd
from threading import Thread
from tvDatafeed import TvDatafeedLive, Interval as TVInterval
from utils.trading_strategy import TradingStrategy
import json
import os

username = ''
password = ''

# Initialize the TradingView API for fetching data
tvl = TvDatafeedLive(username, password)

def get_tv_interval(interval_str):
    interval_map = {
        "1min": TVInterval.in_1_minute,
        "5min": TVInterval.in_5_minute,
        "1hour": TVInterval.in_1_hour
    }
    return interval_map.get(interval_str, TVInterval.in_1_minute)

def get_sleep_time(interval_str):
    interval_map = {
        "1min": 60,
        "5min": 300,
        "1hour": 3600
    }
    return interval_map.get(interval_str, 60)

def fetch_and_update_data(chart, ohlcv_file, signal_system_file, symbol, exchange, config_file):
    last_processed_index = None
    global tvl
    last_config_mtime = 0

    # Initialize the trading strategy
    strategy = TradingStrategy(config_file=config_file)
    
    # Load initial configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    current_interval = config.get('time_interval', '1min')

    while True:
        try:
            # Check if configuration file has been modified
            current_mtime = os.path.getmtime(config_file)
            if current_mtime > last_config_mtime:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                current_interval = config.get('time_interval', '1min')
                strategy = TradingStrategy(config_file=config_file)
                last_config_mtime = current_mtime
                logging.info("Configuration updated")

            # Fetch the latest data based on the current interval
            tv_interval = get_tv_interval(current_interval)
            new_data = tvl.get_hist(symbol, exchange, interval=tv_interval, n_bars=240, fut_contract=None, extended_session=False, timeout=-1)
            
            if new_data is None:
                logging.error("Failed to fetch real-time data")
                raise Exception("Data fetch error")
            
            new_data.reset_index(inplace=True)
            new_data.rename(columns={'datetime': 'date'}, inplace=True)
            new_data['date'] = new_data['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            new_data = new_data[['date', 'open', 'high', 'low', 'close', 'volume']]

            # Calculate indicators using the strategy class
            new_data = strategy.calculate_indicators(new_data)

            # Update the OHLCV file
            try:
                existing_data = pd.read_csv(ohlcv_file)
                updated_data = pd.concat([existing_data, new_data]).drop_duplicates(subset='date', keep='last')
                updated_data = updated_data.reset_index(drop=True)
            except FileNotFoundError:
                updated_data = new_data

            updated_data.fillna(0, inplace=True)
            updated_data.to_csv(ohlcv_file, index=False)
            print("Data loading....")

            # Generate signals directly using the strategy class
            last_processed_index = strategy.generate_signals(updated_data, chart, signal_system_file, ohlcv_file, last_processed_index)

        except Exception as e:
            logging.error(f"Error in fetch_and_update_data: {e}")
            tvl = TvDatafeedLive(username, password)

        # Sleep based on the current interval
        time.sleep(get_sleep_time(current_interval))

# Function to start the data fetching in a separate thread
def start_data_fetching(chart, ohlcv_file, signal_system_file, symbol, exchange, config_file="strategy_config.json"):
    data_thread = Thread(target=fetch_and_update_data, args=(chart, ohlcv_file, signal_system_file, symbol, exchange, config_file))
    data_thread.start()
