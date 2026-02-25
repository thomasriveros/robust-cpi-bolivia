import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

TRACKER_FILE = "tracker_results.json"
OUTPUT_IMAGE = "bolivia_synthetic_cpi_trend.png"

def plot_cpi_trends():
    print("Loading tracker results...")
    try:
        with open(TRACKER_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {TRACKER_FILE} not found. Run daily_tracker.py first.")
        return

    history = data.get("history", [])
    if not history:
        print("No history found in tracker results.")
        return

    # Extract data
    dates = []
    total_cpi = []
    food_cpi = []

    for entry in history:
        # Daily data has "date" as YYYY-MM-DD
        date_str = entry.get("date")
        
        # Parse to datetime for better plotting
        try:
            dt = datetime.fromisoformat(date_str)
        except:
            dt = pd.to_datetime(date_str)
        
        dates.append(dt)
        total_cpi.append(entry.get("cpi"))
        
        # Extract Food CPI
        # Key might vary due to encoding, let's find the one containing "Alimentos"
        sub_indices = entry.get("sub_indices", {})
        food_key = next((k for k in sub_indices.keys() if "Alimentos" in k and "Alcohol" in k), None)
        
        if food_key:
            food_cpi.append(sub_indices[food_key])
        else:
            food_cpi.append(None)

    # Create DataFrame for easier plotting
    df = pd.DataFrame({
        'Date': dates,
        'Total CPI': total_cpi,
        'Food & Beverages': food_cpi
    })
    
    # Sort just in case
    df.sort_values('Date', inplace=True)

    print("Plotting trends...")
    plt.figure(figsize=(10, 6))
    
    plt.plot(df['Date'], df['Total CPI'], marker='o', label='Total synthetic CPI', linewidth=2)
    plt.plot(df['Date'], df['Food & Beverages'], marker='s', linestyle='--', label='Food & Non-Alc. Beverages', linewidth=2)
    
    plt.title('Bolivia Synthetic CPI Trend (Ketal Data)', fontsize=14)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Index (Base = Nov 2021)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE)
    print(f"Plot saved to {OUTPUT_IMAGE}")

if __name__ == "__main__":
    plot_cpi_trends()
