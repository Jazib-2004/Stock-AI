import time
import logging
import pandas as pd
from threading import Thread
from tvDatafeed import TvDatafeedLive, Interval as TVInterval
from utils.trading_strategy import TradingStrategy
import json
import os
username = 'jazibmemon12'
password = 'jazib@123456789000'

# Initialize the TradingView API for fetching data
tvl = TvDatafeedLive(username, password)

def fetch_and_update_data(chart, ohlcv_file, signal_system_file, symbol, exchange, strategy_config_file):
    last_processed_index = None
    global tvl
    
    def check_config_change():
        flag_file = os.path.join('config', f'{os.path.basename(ohlcv_file).split("_")[0]}{os.path.basename(ohlcv_file).split("_")[1]}_config_changed.flag')
        if os.path.exists(flag_file):
            print("Config changed")
            os.remove(flag_file)  # Remove the flag     
            return True
        return False
    
    def get_current_config():
        with open(strategy_config_file, 'r') as f:
            return json.load(f)
    
    def get_interval_settings(config):
        interval_map = {
            "1m": (TVInterval.in_1_minute, 60, 240),
            "5m": (TVInterval.in_5_minute, 300, 48),
            "1h": (TVInterval.in_1_hour, 3600, 24)
        }
        selected_interval = config.get('interval', '1m')
        return interval_map.get(selected_interval, interval_map['1m'])

    # Initial config load
    config = get_current_config()
    interval, sleep_time, n_bars = get_interval_settings(config)
    current_interval = config.get('interval', '1m')  # Track current interval

    # Initialize the trading strategy
    strategy = TradingStrategy(config_file=strategy_config_file)

    while True:
        try:
            if check_config_change():
                new_config = get_current_config()
                if new_config.get('interval') != config.get('interval'):
                    logging.info(f"Interval changed from {config.get('interval')} to {new_config.get('interval')}")
                    config = new_config
                    interval, sleep_time, n_bars = get_interval_settings(config)
                    strategy = TradingStrategy(config_file=strategy_config_file)
                    current_interval = new_config.get('interval', '1m')  # Update current interval
                    # Clear existing data when interval changes
                    if os.path.exists(ohlcv_file):
                        os.remove(ohlcv_file)
                        logging.info(f"Cleared existing data due to interval change to {current_interval}")

            # Fetch the latest data
            new_data = tvl.get_hist(symbol, exchange, interval=interval, n_bars=240, 
                                  fut_contract=None, extended_session=False, timeout=-1)
            if new_data is None:
                logging.error("Failed to fetch real-time data")
                raise Exception("Data fetch error")
            
            new_data.reset_index(inplace=True)
            new_data.rename(columns={'datetime': 'date'}, inplace=True)
            new_data['date'] = new_data['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            new_data = new_data[['date', 'open', 'high', 'low', 'close', 'volume']]
            new_data['interval'] = current_interval  # Add interval information

            # Calculate indicators using the strategy class
            new_data = strategy.calculate_indicators(new_data)

            # Update the OHLCV file
            try:
                if os.path.exists(ohlcv_file):
                    existing_data = pd.read_csv(ohlcv_file)
                    # Only concatenate if intervals match
                    if existing_data['interval'].iloc[0] == current_interval:
                        updated_data = pd.concat([existing_data, new_data]).drop_duplicates(subset='date', keep='last')
                    else:
                        updated_data = new_data
                else:
                    updated_data = new_data

                updated_data = updated_data.reset_index(drop=True)
                updated_data.fillna(0, inplace=True)
                updated_data.to_csv(ohlcv_file, index=False)
                logging.info(f"Data updated successfully for {current_interval} interval")

            except Exception as e:
                logging.error(f"Error updating OHLCV file: {e}")
                updated_data = new_data
                updated_data.to_csv(ohlcv_file, index=False)

            # Generate signals directly using the strategy class
            last_processed_index = strategy.generate_signals(updated_data, chart, signal_system_file, ohlcv_file, last_processed_index)

        except Exception as e:
            logging.error(f"Error in fetch_and_update_data: {e}")
            tvl = TvDatafeedLive(username, password)

        time.sleep(sleep_time)

# Function to start the data fetching in a separate thread
def start_data_fetching(chart, ohlcv_file, signal_system_file, symbol, exchange, strategy_config_file="strategy_config.json"):
    data_thread = Thread(target=fetch_and_update_data, args=(chart, ohlcv_file, signal_system_file, symbol, exchange, strategy_config_file))
    data_thread.start()
