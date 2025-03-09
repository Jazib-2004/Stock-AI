import csv
import subprocess
import os
import sys
import pandas as pd
import signal
import psutil
from ui_controller import TradingAppUI

def get_virtual_env_python():
    """Return the path to the Python interpreter in the current virtual environment."""
    return sys.executable

def run_stock_ai(symbol, exchange, title, filename):
    """Run the stock_ai.py script with the given parameters using the virtual environment's Python interpreter."""
    python_executable = get_virtual_env_python()
    try:
            
        process = subprocess.Popen([python_executable, 'stock_ai.py', symbol, exchange, title, filename])
        return process
    except Exception as e:
        print(f"Error starting process: {e}")
        return None

def load_targets_and_run():
    """Load targets from CSV and run the stock_ai.py script for each."""
    ui = TradingAppUI()
    running_processes = []

    def on_start_trading(event):
        with open(os.path.join('config', 'targets.csv'), mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = row['Symbol']
                exchange = row['Exchange']
                title = row['Title']
                filename = row['Filename']
                print(f"Running stock_ai.py for {symbol} on {exchange}...")
                process = run_stock_ai(symbol, exchange, title, filename)
                if process is not None:
                    running_processes.append(process)

    def on_stop_trading(event):
        for process in running_processes:
            try:
                if process is not None:
                    # Get the process ID
                    pid = process.pid
                    
                    # Get the parent process and all its children
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    
                    # Terminate children first
                    for child in children:
                        try:
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                    
                    # Terminate the parent process
                    if parent.is_running():
                        parent.terminate()
                    
                    # If processes are still alive, kill them forcefully
                    gone, alive = psutil.wait_procs(children + [parent], timeout=3)
                    for p in alive:
                        try:
                            p.kill()  # Forcefully kill if still running
                        except psutil.NoSuchProcess:
                            pass
                    
            except Exception as e:
                print(f"Error stopping process: {e}")        
        running_processes.clear()
        print("All trading processes stopped")
    
    # Bind the start trading event
    ui.root.bind('<<StartTrading>>', on_start_trading)
    ui.root.bind('<<StopTrading>>', on_stop_trading)

    # Run the UI
    ui.run()

def combine_signal_files():
    """Combine all signal system files into a single data/result.csv with a PAIR column first and sorted by Buy Time."""
    target_file = os.path.join('data', 'result.csv')
    all_data = []

    # Load targets from CSV
    with open(os.path.join('config', 'targets.csv'), mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = row['Title']
            filename = row['Filename']
            
            signal_system_file = os.path.join('data', f"{filename}_Signal_system.csv")
            
            if os.path.exists(signal_system_file):
                # Read each signal system file and add the "PAIR" column
                data = pd.read_csv(signal_system_file)
                data['PAIR'] = f"{title}"
                all_data.append(data)
            else:
                print(f"Warning: {signal_system_file} does not exist.")

    if all_data:
        # Combine all data into a single DataFrame
        combined_data = pd.concat(all_data, ignore_index=True)

        # Reorder columns to have "PAIR" first
        columns = ['PAIR', 'Buy Time', 'Buy Price', 'Take Profit', 'Stop Loss', 'Close', 'Close Time', '%']
        combined_data = combined_data[columns]

        # Sort by "Buy Time"
        combined_data.sort_values(by=['Buy Time'], inplace=True)

        # Save to data/result.csv
        combined_data.to_csv(target_file, index=False)
        print(f"Combined result saved to {target_file}.")
    else:
        print("No data to combine.")

if __name__ == '__main__':
    combine_signal_files()
    load_targets_and_run()
