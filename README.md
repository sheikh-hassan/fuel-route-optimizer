# 🚗⛽ Fuel Route Optimizer

An optimized Django API that returns the **cheapest fuel stops** along a driving route in the **USA**, using **OpenRouteService** and a geocoded fuel price dataset.


## 🔧 Features

* ⚡ **High-performance routing** using spatial indexing (`cKDTree`)
* ⛽ **Vehicle range-aware optimization** (default: 500 miles per tank)
* 🗺️ **Single API call** per request using OpenRouteService (ORS)
* 🧭 Returns:

  * Optimized route geometry
  * Major driving steps
  * Cheapest fuel stops
* 📍 Uses geocoded data from \~8,000 U.S. fuel stations


## 📦 Tech Stack

* **Python 3.9+**
* **Django 3.2.23**
* **Django REST Framework**
* **OpenRouteService API**
* **Pandas, NumPy, SciPy**
* **GeoPy**


## 🚀 Setup Instructions

```bash
# Clone the repository
git clone https://github.com/sheikh-hassan/fuel-route-optimizer.git
cd fuel-route-optimizer

# Create and activate a virtual environment
python -m venv env
source env/bin/activate          # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env
```


## 🔐 Environment Variables

Edit your `.env` file to include your [OpenRouteService](https://openrouteservice.org/dev/#/signup) API key:

```env
ORS_API_KEY="your_openrouteservice_api_key_here"
GOOGLE_MAPS_API_KEY="your_google_maps_api_key_here"
```


## 📊 Fuel Data Files

The app uses two main CSV files located in the `data/` folder:

| File                                | Description                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------ |
| `fuel-prices-for-be-assessment.csv` | Original dataset with truck stop names, addresses, and prices (no coordinates) |
| `fuel-prices-geocoded.csv`          | Geocoded version with latitude and longitude — **used by the app**             |

No runtime geocoding is needed — the app uses the preprocessed file for fast spatial queries.

## 🧪 API Usage

**Endpoint**: `POST /route/`

### ✅ Request Body (JSON)

```json
{
  "start": "Chicago, IL",
  "end": "Dallas, TX"
}
```

### ✅ Response

* Start and end coordinates
* Total route distance
* Optimized fuel stops with cost breakdown
* GeoJSON route with navigation steps


## 📁 Directory Structure

```
fuel-route-optimizer/
│
├── data/
│   ├── fuel-prices-for-be-assessment.csv
│   └── fuel-prices-geocoded.csv
├── env/                 ← Virtual environment
├── fuel_app/            ← Django app logic
├── manage.py
├── requirements.txt
└── .env.example
```
