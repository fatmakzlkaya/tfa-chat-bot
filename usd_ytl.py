import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
from evds import evdsAPI

load_dotenv()
api_key = os.getenv("TCMB_API_KEY")
if not api_key:
    raise ValueError("API_KEY didn't find.")
today = datetime.now()
one_year_ago = today - timedelta(days=365)

evds = evdsAPI(api_key)
series_code = "TP.DK.USD.A.YTL"    # Annual USD Change
start_date = one_year_ago.strftime("%d-%m-%Y") 
end_date = today.strftime("%d-%m-%Y")

try:
    usd_try_df = evds.get_data([series_code], start_date, end_date)
except requests.exceptions.RequestException as e:
    print(f"An error occurred during the API request: {e}")
    usd_try_df = pd.DataFrame()  # Prevent crash if request fails

if not usd_try_df.empty:
    # Fill missing values
    usd_try_df = usd_try_df.ffill()


    # Get the first and last exchange rate values
    old = usd_try_df['TP_DK_USD_A_YTL'].iloc[0]
    new = usd_try_df['TP_DK_USD_A_YTL'].iloc[-1]

    # Calculate absolute and percentage changes
    difference = new - old
    change_percent = (difference / old) * 100

    # Print results
    print(f"💵 Your 1 dollar was {old:.2f} TL")
    print(f"💵 Now it is {new:.2f} TL")
    
    emoji = "📈" if difference >= 0 else "📉"
    print(f"{emoji} Change: {difference:.2f} TL ({change_percent:+.2f}%)")


    # Convert 'Tarih' to datetime and drop any invalid rows
    usd_try_df['Tarih'] = pd.to_datetime(usd_try_df['Tarih'], format="%d-%m-%Y", errors='coerce')
    usd_try_df = usd_try_df.dropna(subset=['Tarih', 'TP_DK_USD_A_YTL'])
    usd_try_df = usd_try_df.sort_values('Tarih')
    # Plot the data using the cleaned 'Tarih' column
    plt.figure(figsize=(12, 6))
    plt.plot(usd_try_df['Tarih'], usd_try_df['TP_DK_USD_A_YTL'], marker='o', linestyle='-')
    plt.title("USD/TRY Time Series", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Exchange Rate (TRY)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

else:
    print("No data retrieved or API response is empty.")
