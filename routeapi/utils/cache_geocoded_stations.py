import pandas as pd
import requests
import time
import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
INPUT_CSV = "fuel-prices-for-be-assessment.csv"
OUTPUT_CSV = "fuel-prices-geocoded.csv"

def geocode_address(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None

def main():
    # Load original dataset
    df = pd.read_csv(INPUT_CSV)

    # Check for existing geocoded file to resume
    if os.path.exists(OUTPUT_CSV):
        print("📂 Resuming from existing output file...")
        geocoded_df = pd.read_csv(OUTPUT_CSV)
    else:
        print("🆕 Starting fresh...")
        geocoded_df = df.copy()
        geocoded_df["latitude"] = None
        geocoded_df["longitude"] = None

    # Iterate through all rows
    for i, row in geocoded_df.iterrows():
        if pd.notnull(row["latitude"]) and pd.notnull(row["longitude"]):
            continue  # Already processed

        full_address = f"{row['Address']}, {row['City']}, {row['State']}, USA"
        print(f"📍 Geocoding ({i+1}/{len(df)}): {full_address}")

        lat, lng = geocode_address(full_address)
        if lat is not None and lng is not None:
            geocoded_df.at[i, "latitude"] = lat
            geocoded_df.at[i, "longitude"] = lng
            print(f"✅ Success: {lat}, {lng}")
        else:
            print(f"❌ Failed to geocode: {full_address}")

        # Save progress every 10 rows
        if i % 10 == 0:
            geocoded_df.to_csv(OUTPUT_CSV, index=False)

        # Respect Google Maps API rate limits
        time.sleep(0.2)

    # Final save
    geocoded_df.to_csv(OUTPUT_CSV, index=False)
    print("✅ All done. Geocoded file saved as:", OUTPUT_CSV)

if __name__ == "__main__":
    main()
