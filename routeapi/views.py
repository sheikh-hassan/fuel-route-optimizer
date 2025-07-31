from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import openrouteservice
from geopy.distance import geodesic
import os
from dotenv import load_dotenv
from .utils.fuel_cache import stations_df, coords, tree

# Load OpenRouteService API key from environment
load_dotenv()
client = openrouteservice.Client(key=os.getenv("ORS_API_KEY"))


@api_view(['POST'])
def route_view(request):
    start = request.data.get('start')
    end = request.data.get('end')

    # Validate input
    if not start or not end:
        return Response({"error": "Start and end locations are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Geocode start and end locations
    try:
        start_coords = client.pelias_search(text=start)['features'][0]['geometry']['coordinates'][::-1]
        end_coords = client.pelias_search(text=end)['features'][0]['geometry']['coordinates'][::-1]
    except:
        return Response({"error": "Failed to geocode start or end location."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch route between start and end
    try:
        route = client.directions(
            coordinates=[start_coords[::-1], end_coords[::-1]],
            profile='driving-car',
            format='geojson'
        )

        # Downsample geometry if too long to reduce payload size
        coordinates = route['features'][0]['geometry']['coordinates']
        if len(coordinates) > 500:
            route['features'][0]['geometry']['coordinates'] = coordinates[::10]
    except:
        return Response({"error": "Failed to fetch route."}, status=status.HTTP_502_BAD_GATEWAY)

    # Extract route coordinates in (lat, lng) format
    route_coords = [(lat, lng) for lng, lat in route['features'][0]['geometry']['coordinates']]
    total_distance_miles = route['features'][0]['properties']['summary']['distance'] / 1609.34

    # Vehicle parameters
    vehicle_range_miles = 500
    mpg = 10
    tank_capacity = 50

    # Initialize fuel stop search
    fuel_stops = []
    accumulated_distance = 0
    seen_stations = set()

    # Walk through the route to determine fuel stops
    for i in range(1, len(route_coords)):
        seg_distance = geodesic(route_coords[i - 1], route_coords[i]).miles
        accumulated_distance += seg_distance

        if accumulated_distance >= vehicle_range_miles or i == len(route_coords) - 1:
            lat, lng = route_coords[i]

            # Find nearby fuel stations within ~10 miles (0.2° radius)
            matches = tree.query_ball_point([lat, lng], r=0.2)

            if matches:
                nearby = stations_df.iloc[matches].copy()
                nearby = nearby[~nearby['Truckstop Name'].isin(seen_stations)]

                if not nearby.empty:
                    best = nearby.sort_values('Retail Price').iloc[0]
                    seen_stations.add(best['Truckstop Name'])

                    gallons_needed = accumulated_distance / mpg
                    gallons_to_fill = min(tank_capacity, gallons_needed)
                    cost = gallons_to_fill * best['Retail Price']

                    fuel_stops.append({
                        "location": {
                            "name": best['Truckstop Name'],
                            "lat": best['latitude'],
                            "lng": best['longitude']
                        },
                        "price_per_gallon": round(best['Retail Price'], 3),
                        "fuel_cost": round(cost, 2),
                        "filled_gallons": round(gallons_to_fill, 2)
                    })

                    accumulated_distance = 0  # Reset distance after refuel

    total_fuel_cost = round(sum(stop['fuel_cost'] for stop in fuel_stops), 2)

    # Optionally reduce step verbosity in instructions
    def filter_major_steps(steps, min_distance=1000, include_types={0, 1, 6, 12, 13}):
        return [
            step for step in steps
            if step["distance"] >= min_distance or step["type"] in include_types
        ]

    route_data = route['features'][0]

    # Reduce unnecessary step data for clarity and payload size
    if 'segments' in route_data.get('properties', {}):
        for segment in route_data['properties']['segments']:
            if 'steps' in segment:
                segment['steps'] = filter_major_steps(segment['steps'])

    # Ensure geometry is still compact
    geometry = route_data.get('geometry', {})
    if 'coordinates' in geometry:
        geometry['coordinates'] = geometry['coordinates'][::10]

    # Build final response
    response_data = {
        "start_coords": start_coords,
        "end_coords": end_coords,
        "total_distance_miles": round(total_distance_miles, 2),
        "fuel_stops": [] if total_distance_miles <= vehicle_range_miles else fuel_stops,
        "total_fuel_cost": 0.0 if total_distance_miles <= vehicle_range_miles else total_fuel_cost,
        "route_geojson": route_data
    }

    return Response(response_data)
