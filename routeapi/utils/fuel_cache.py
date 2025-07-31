import os
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from django.conf import settings

# Path to the geocoded fuel prices CSV
FUEL_CSV_PATH = os.path.join(settings.BASE_DIR, 'data', 'fuel-prices-geocoded.csv')

# Load fuel station data
stations_df = pd.read_csv(FUEL_CSV_PATH)

# Confirm required columns are present
required_columns = ['latitude', 'longitude']
if not all(col in stations_df.columns for col in required_columns):
    raise ValueError(f"Missing one or more required columns: {required_columns}")

# Remove entries with missing or invalid coordinates
stations_df = stations_df.dropna(subset=['latitude', 'longitude'])
stations_df = stations_df[stations_df['latitude'].apply(np.isfinite)]
stations_df = stations_df[stations_df['longitude'].apply(np.isfinite)]

# Prepare coordinates for KDTree indexing
coords = stations_df[['latitude', 'longitude']].to_numpy()

# Final check for any remaining invalid values
if not np.all(np.isfinite(coords)):
    raise ValueError("Non-finite coordinates still present after filtering.")

# Build KDTree for fast geospatial lookup
tree = cKDTree(coords)

# Expose cleaned DataFrame and KDTree for use across the app
FUEL_STATIONS_DF = stations_df.reset_index(drop=True)
FUEL_KD_TREE = tree
