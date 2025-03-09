import pandas as pd
from lightweight_charts import Chart
from utils.logging_utils import logging
import time
from functools import partial
import json
import os
def on_max(target_chart, charts):
    button = target_chart.topbar['max']
    if button.value == '×':
        for c in charts:
            width, height = (1, 0.4) if c == charts[0] else (1, 0.2)
            c.resize(width, height)
        button.set('■')
    else:
        for c in charts:
            width, height = (1, 1) if c == target_chart else (0, 0)
            c.resize(width, height)
        button.set('×')

def draw_chart(title, ohlcv_file):
    logging.info("Initializing chart...")
    chart = Chart(inner_width=1, inner_height=0.4)
    chart.legend(visible=True)
    chart.topbar.textbox('symbol', title)  # Use the dynamic title

    rsi_chart = chart.create_subchart(width=1, height=0.2)
    rsi_chart.topbar.textbox('symbol', 'RSI')
    rsi_line = rsi_chart.create_line(name='RSI', color="rgb(126, 87, 194)")

    macd_chart = chart.create_subchart(width=1, height=0.2)
    macd_chart.topbar.textbox('symbol', 'MACD')
    macd_line = macd_chart.create_line(name='MACD', color="rgb(41, 98, 255)")
    macd_signal_line = macd_chart.create_line(name='MACD Signal', color="rgb(255, 109, 0)")
    macd_histogram_series = macd_chart.create_histogram('MACD Histogram')    

    stochrsi_chart = chart.create_subchart(width=1, height=0.2)
    stochrsi_chart.topbar.textbox('symbol', 'StochRSI')
    stochrsi_k_line = stochrsi_chart.create_line(name='StochRSI %K', color="rgb(255,255,255)")
    stochrsi_d_line = stochrsi_chart.create_line(name='StochRSI %D', color="rgb(255,0,255)")

    charts = [chart, rsi_chart, macd_chart, stochrsi_chart]

    for i, c in enumerate(charts):
        chart_number = str(i + 1)
        c.topbar.button('max', '■', False, align='right', func=lambda _chart=c: on_max(_chart, charts))

    # Load and set data as before
    try:
        logging.info(f"Loading data from {ohlcv_file}...")
        df = pd.read_csv(ohlcv_file)
        if df.empty:
            logging.warning(f"No data found in {ohlcv_file}. Chart might not render.")
        else:
            chart.set(df[['date', 'open', 'high', 'low', 'close', 'volume']])

            rsi_data = df[['date', 'rsi']].rename(columns={'rsi': 'RSI'})
            rsi_line.set(rsi_data)

            macd_data = df[['date', 'macd']].rename(columns={'macd': 'MACD'})
            macd_line.set(macd_data)

            macd_signal_data = df[['date', 'macd_signal']].rename(columns={'macd_signal': 'MACD Signal'})
            macd_signal_line.set(macd_signal_data)

            macd_histogram_data = df[['date', 'macd_hist']].rename(columns={'macd_hist': 'MACD Histogram'})
            macd_histogram_series.set(macd_histogram_data)

            stochrsi_k_data = df[['date', 'stochrsi_K']].rename(columns={'stochrsi_K': 'StochRSI %K'})
            stochrsi_k_line.set(stochrsi_k_data)

            stochrsi_d_data = df[['date', 'stochrsi_D']].rename(columns={'stochrsi_D': 'StochRSI %D'})
            stochrsi_d_line.set(stochrsi_d_data)

        logging.info("Chart initialized successfully.")

    except FileNotFoundError:
        logging.error(f"{ohlcv_file} not found. Please ensure data fetching is working correctly.")

    return chart, rsi_line, macd_line, macd_signal_line, macd_histogram_series, stochrsi_k_line, stochrsi_d_line

def update_chart_and_indicators(chart, rsi_line, macd_line, macd_signal_line, macd_histogram_series, stochrsi_k_line, stochrsi_d_line, ohlcv_file):
    def check_config_change():
        flag_file = os.path.join('config', f'{os.path.basename(ohlcv_file).split("_")[0]}{os.path.basename(ohlcv_file).split("_")[1]}_config_changed.flag')
        if os.path.exists(flag_file):
            print("Config changed")
            return True
        return False
    
    # Load the strategy config to get the interval
    with open(os.path.join('config', 'strategy_config.json'), 'r') as f:
        config = json.load(f)
    
    # Get update interval from config
    interval_map = {
        "1m": 60,    # 60 seconds for 1-minute interval
        "5m": 300,   # 300 seconds for 5-minute interval
        "1h": 3600   # 3600 seconds for 1-hour interval
    }
    interval = interval_map.get(config.get('interval', '1m'), 60)

    while True:
        try:
            # Check for config changes
            if check_config_change():
                with open(os.path.join('config', 'strategy_config.json'), 'r') as f:
                    new_config = json.load(f)
                if new_config.get('interval') != config.get('interval'):
                    config = new_config
                    interval = interval_map.get(config.get('interval', '1m'), 60)
                    logging.info(f"Chart update interval changed to {interval} seconds")

            df = pd.read_csv(ohlcv_file)
            
            # Update main chart
            chart.set(df[['date', 'open', 'high', 'low', 'close', 'volume']])

            # Update RSI
            rsi_data = df[['date', 'rsi']].rename(columns={'rsi': 'RSI'})
            rsi_line.set(rsi_data)

            # Update MACD
            macd_data = df[['date', 'macd']].rename(columns={'macd': 'MACD'})
            macd_line.set(macd_data)

            macd_signal_data = df[['date', 'macd_signal']].rename(columns={'macd_signal': 'MACD Signal'})
            macd_signal_line.set(macd_signal_data)

            macd_histogram_data = df[['date', 'macd_hist']].rename(columns={'macd_hist': 'MACD Histogram'})
            macd_histogram_series.set(macd_histogram_data)

            # Update StochRSI
            stochrsi_k_data = df[['date', 'stochrsi_K']].rename(columns={'stochrsi_K': 'StochRSI %K'})
            stochrsi_k_line.set(stochrsi_k_data)

            stochrsi_d_data = df[['date', 'stochrsi_D']].rename(columns={'stochrsi_D': 'StochRSI %D'})
            stochrsi_d_line.set(stochrsi_d_data)

            logging.info(f"Chart updated successfully for {config.get('interval', '1m')} interval.")

            
        except Exception as e:
            logging.error(f"Error updating chart: {e}")

        time.sleep(interval)