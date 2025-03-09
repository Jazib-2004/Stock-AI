import tkinter as tk
from tkinter import ttk
import json
import os
from threading import Event

class ConfigGUI:
    def __init__(self, config_update_event):
        self.root = tk.Tk()
        self.root.title("Trading Configuration")
        self.root.geometry("300x200")
        
        self.config_update_event = config_update_event
        
        # Create and set up the GUI elements
        self.setup_gui()
        
        # Load initial values
        self.load_config()

    def setup_gui(self):
        # Take Profit Frame
        tp_frame = ttk.LabelFrame(self.root, text="Take Profit", padding="5")
        tp_frame.pack(fill="x", padx=5, pady=5)
        
        self.tp_var = tk.StringVar()
        tp_entry = ttk.Entry(tp_frame, textvariable=self.tp_var)
        tp_entry.pack(fill="x", padx=5)
        
        ttk.Label(tp_frame, text="Enter value between 1.0 and 2.0").pack()

        # Time Interval Frame
        interval_frame = ttk.LabelFrame(self.root, text="Time Interval", padding="5")
        interval_frame.pack(fill="x", padx=5, pady=5)
        
        self.interval_var = tk.StringVar()
        intervals = ["1min", "5min", "1hour"]
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var, values=intervals)
        interval_combo.pack(fill="x", padx=5)

        # Apply Button
        apply_btn = ttk.Button(self.root, text="Apply Changes", command=self.apply_changes)
        apply_btn.pack(pady=10)

    def load_config(self):
        try:
            with open("strategy_config.json", "r") as f:
                config = json.load(f)
                self.tp_var.set(str(config.get("take_profit", 2.0)))
                self.interval_var.set(config.get("time_interval", "1min"))
        except FileNotFoundError:
            self.tp_var.set("2.0")
            self.interval_var.set("1min")
            self.save_config()

    def save_config(self):
        config = {
            "take_profit": float(self.tp_var.get()),
            "time_interval": self.interval_var.get()
        }
        with open("strategy_config.json", "w") as f:
            json.dump(config, f, indent=4)

    def validate_inputs(self):
        try:
            tp = float(self.tp_var.get())
            if not (1.0 <= tp <= 2.0):
                return False, "Take Profit must be between 1.0 and 2.0"
            
            interval = self.interval_var.get()
            if interval not in ["1min", "5min", "1hour"]:
                return False, "Invalid time interval"
                
            return True, None
        except ValueError:
            return False, "Invalid Take Profit value"

    def apply_changes(self):
        valid, error_msg = self.validate_inputs()
        if not valid:
            tk.messagebox.showerror("Error", error_msg)
            return
            
        self.save_config()
        # Signal that configuration has been updated
        self.config_update_event.set()

    def run(self):
        self.root.mainloop()