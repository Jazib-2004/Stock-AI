import tkinter as tk
from tkinter import ttk
import json
import webbrowser
from datetime import datetime
import os
from tvDatafeed import Interval as TVInterval
import csv
from PIL import Image, ImageTk

class TradingAppUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trading Bot Control Panel")
        self.root.geometry("900x700") 
        
        # Define theme colors
        self.colors = {
            'bg': '#1E2329',          # Dark background
            'frame_bg': '#262B32',    # Slightly lighter background for frames
            'text': '#E6E8EA',        # Light text
            'accent': '#02C076',      # Green accent for buttons/highlights
            'border': '#363A45'       # Border color
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg'])
        
        # Configure styles
        self.setup_styles()
        
        # Initialize variables
        self.take_profit_var = tk.StringVar(value="2.0")
        self.stop_loss_var = tk.StringVar(value="1.0")
        self.interval_var = tk.StringVar(value="1m")
        
        # Load initial config
        self.load_config()
        
        # Create UI elements
        self.create_widgets()
        
        # Flag to track if trading has started
        self.trading_started = False

    def setup_styles(self):
        style = ttk.Style()
        
        # Configure frame styles
        style.configure('Main.TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['frame_bg'])
        
        # Configure labelframe styles
        style.configure('Card.TLabelframe', 
                    background=self.colors['frame_bg'],
                    foreground=self.colors['text'])
        style.configure('Card.TLabelframe.Label', 
                    background=self.colors['frame_bg'],
                    foreground=self.colors['text'],
                    font=('Helvetica', 10, 'bold'))
        
        # Configure label styles
        style.configure('Card.TLabel',
                    background=self.colors['frame_bg'],
                    foreground=self.colors['text'],
                    font=('Helvetica', 10))
        
        # Configure entry styles
        style.configure('Card.TEntry', 
                    fieldbackground=self.colors['bg'],
                    foreground=self.colors['frame_bg'])
        
        # Configure button styles
        style.configure('Accent.TButton',
                    background=self.colors['accent'],
                    foreground=self.colors['frame_bg'],
                    font=('Helvetica', 10, 'bold'),
                    padding=5)
        
        # Configure radiobutton styles
        style.configure('Card.TRadiobutton',
                    background=self.colors['frame_bg'],
                    foreground=self.colors['text'],
                    font=('Helvetica', 10))

    def create_widgets(self):
        # Create main container with padding
        main_container = ttk.Frame(self.root, style='Main.TFrame')
        main_container.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Left panel for controls
        left_panel = ttk.LabelFrame(main_container, text="Trading Controls", 
                                style='Card.TLabelframe', padding="15")
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Profit Settings Section with rounded corners
        profit_frame = ttk.LabelFrame(left_panel, text="Profit Settings", 
                                    style='Card.TLabelframe', padding="15")
        profit_frame.pack(fill="x", pady=10, padx=5)
        
        ttk.Label(profit_frame, text="Take Profit (%)", 
                style='Card.TLabel').pack(anchor="w")
        profit_entry = ttk.Entry(profit_frame, textvariable=self.take_profit_var, 
                            style='Card.TEntry', width=35)
        profit_entry.pack(fill="x", pady=5)
        
        ttk.Label(profit_frame, text="Stop Loss (%)", 
                style='Card.TLabel').pack(anchor="w")
        loss_entry = ttk.Entry(profit_frame, textvariable=self.stop_loss_var, 
                            style='Card.TEntry', width=35)
        loss_entry.pack(fill="x", pady=5)
        
        # Time Interval Section
        interval_frame = ttk.LabelFrame(left_panel, text="Time Interval", 
                                    style='Card.TLabelframe', padding="15")
        interval_frame.pack(fill="x", pady=10, padx=5)
        
        intervals = [("1 Minute", "1m"), ("5 Minutes", "5m"), ("1 Hour", "1h")]
        for text, value in intervals:
            ttk.Radiobutton(interval_frame, text=text, value=value,
                        variable=self.interval_var,
                        command=self.on_interval_change,
                        style='Card.TRadiobutton').pack(anchor="w", pady=3)
        
        # Control Buttons
        button_frame = ttk.Frame(left_panel, style='Card.TFrame')
        button_frame.pack(fill="x", pady=10, padx=5)
        
        self.start_button = ttk.Button(button_frame, text="Start Trading",
                                    command=self.start_trading,
                                    style='Accent.TButton')
        self.start_button.pack(fill="x", pady=3)
        
        ttk.Button(button_frame, text="Apply Changes",
                command=self.apply_changes,
                style='Accent.TButton').pack(fill="x", pady=3)
        
        ttk.Button(button_frame, text="Export Results",
                command=self.export_results,
                style='Accent.TButton').pack(fill="x", pady=3)
        
        # Status Frame
        self.status_frame = ttk.LabelFrame(left_panel, text="Status", 
                                        style='Card.TLabelframe', padding="15")
        self.status_frame.pack(fill="x", pady=10, padx=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready to start trading",
                                    style='Card.TLabel')
        self.status_label.pack(fill="x")
        
        # Right panel for image
        right_panel = ttk.Frame(main_container, style='Main.TFrame')
        right_panel.pack(side="right", fill="both", expand=True, padx=5)
        
        try:
            # Load and resize the image
            image = Image.open('assets/trading-logo.png')
            desired_width = 350  # Slightly smaller width
            aspect_ratio = image.height / image.width
            desired_height = int(desired_width * aspect_ratio)
            
            image = image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            self.trading_photo = ImageTk.PhotoImage(image)
            
            # Create frame for vertical centering
            image_container = ttk.Frame(right_panel, style='Main.TFrame')
            image_container.pack(expand=True)
            
            # Create label with image
            image_label = ttk.Label(image_container, image=self.trading_photo, 
                                background=self.colors['bg'])
            image_label.pack()
            
            # Caption below image
            caption = ttk.Label(image_container, 
                            text="AI-Powered Trading System",
                            style='Card.TLabel',
                            font=('Helvetica', 12, 'bold'))
            caption.pack(pady=10)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            fallback_container = ttk.Frame(right_panel, style='Main.TFrame')
            fallback_container.pack(expand=True)
            ttk.Label(fallback_container, 
                    text="AI Trading Bot\nPowered by Advanced Analytics",
                    style='Card.TLabel',
                    font=('Helvetica', 14, 'bold'),
                    justify='center').pack()
        
    
    def signal_config_change(self,symbol):
        """Create a flag file to signal configuration change for a specific symbol"""
        flag_file = os.path.join('config', f'{symbol}_config_changed.flag')
        try:
            with open(flag_file, 'w') as f:
                f.write('1')
        except Exception as e:
            print(f"Error creating flag file: {e}")  
    def load_config(self):
        try:
            with open(os.path.join('config', 'strategy_config.json'), 'r') as f:
                config = json.load(f)
                self.take_profit_var.set(str(config.get('take_profit', 2.0)))
                self.stop_loss_var.set(str(config.get('stop_loss', 1.0)))
                self.interval_var.set(config.get('interval', '1m'))
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        config = {
            "take_profit": float(self.take_profit_var.get()),
            "stop_loss": float(self.stop_loss_var.get()),
            "interval": self.interval_var.get(),
            "rsi_period": 14,
            "stochrsi_period": 14,
            "macd_fast_period": 12,
            "macd_slow_period": 26,
            "macd_signal_period": 9,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "stochrsi_overbought": 80,
            "stochrsi_oversold": 20
        }
        
        with open(os.path.join('config', 'strategy_config.json'), 'w') as f:
            json.dump(config, f, indent=2)
        
        self.update_status("Configuration saved successfully")

    def start_trading(self):
        if not self.trading_started:
            self.save_config()
            self.trading_started = True
            self.start_button.configure(text="Stop Trading")
            self.update_status("Trading started")
            
            # Signal to main.py to start trading
            self.root.event_generate('<<StartTrading>>')
        else:
            self.trading_started = False
            self.start_button.configure(text="Start Trading")
            self.update_status("Trading stopped")
            # Signal to main.py to stop trading
            self.root.event_generate('<<StopTrading>>')
    
    
    def apply_changes(self):
        self.save_config()
        with open(os.path.join('config', 'targets.csv'), mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = row['Symbol']
                self.signal_config_change(symbol)
        self.update_status("Changes applied successfully")
    
    def on_interval_change(self):
        if self.trading_started:
            self.save_config()
            self.update_status(f"Interval changed to {self.interval_var.get()}")
    
    def update_status(self, message):
        self.status_label.config(text=message)
        
    def export_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join('exports', f'trading_results_{timestamp}.csv')
        
        os.makedirs('exports', exist_ok=True)
        
        if os.path.exists(os.path.join('data', 'result.csv')):
            import shutil
            shutil.copy2(os.path.join('data', 'result.csv'), export_path)
            webbrowser.open(export_path)
            self.update_status(f"Results exported to {export_path}")
        else:
            self.update_status("No results available to export")
    
    def run(self):
        self.root.mainloop()
        return self.trading_started