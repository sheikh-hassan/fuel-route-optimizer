# Fuel Route Optimizer 🚗⛽

An optimized Django API that returns the cheapest fuel stops along a driving route in the USA using OpenRouteService and a provided fuel price dataset.

## 🔧 Features
- Fast route and fuel stop optimization using spatial search (cKDTree)
- Vehicle range aware (500 miles max range)
- Uses OpenRouteService for geocoding & routing (1 API call per request)
- Returns route geometry + instructions + fuel stations
- Geocoded fuel dataset (~8000 stations)

## 📦 Tech Stack
- Django 3.2.23
- Python 3.9+
- REST Framework
- OpenRouteService API
- Pandas, NumPy, SciPy (KDTree)
- GeoPy

## 🚀 Setup Instructions

```bash
git clone https://github.com/yourusername/fuel-route-optimizer.git
cd fuel-route-optimizer
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
