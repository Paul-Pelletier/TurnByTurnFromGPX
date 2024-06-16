import gpxpy
import gpxpy.gpx
import googlemaps
import os
import numpy as np
from geopy.distance import geodesic
from scipy.spatial.distance import directed_hausdorff
import random
import folium

def parse_gpx(file_path):
    # Parse the GPX file
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    waypoints = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                waypoints.append((point.latitude, point.longitude))
    return waypoints

def generate_google_maps_route(api_key, waypoints, mode="bicycling"):
    gmaps = googlemaps.Client(key=api_key)
    
    # Limit waypoints to a maximum of 23 (Google Maps API limit)
    max_waypoints = 23
    if len(waypoints) > max_waypoints:
        waypoints = random.sample(waypoints[:-1], max_waypoints - 2)  # Randomly sample waypoints
        waypoints = [waypoints[0]] + waypoints + [waypoints[-1]]
    
    origin = waypoints[0]
    destination = waypoints[-1]
    waypoints = waypoints[1:-1]

    result = gmaps.directions(
        origin,
        destination,
        mode=mode,
        waypoints=waypoints,
        optimize_waypoints=True
    )

    if not result:
        raise ValueError("No route found.")

    # Extract route points from Google Maps Directions result
    route_points = []
    for leg in result[0]['legs']:
        for step in leg['steps']:
            start_location = step['start_location']
            route_points.append((start_location['lat'], start_location['lng']))
            end_location = step['end_location']
            route_points.append((end_location['lat'], end_location['lng']))

    # Generate Google Maps URL
    url = "https://www.google.com/maps/dir/?api=1"
    url += f"&origin={origin[0]},{origin[1]}"
    url += f"&destination={destination[0]},{destination[1]}"
    waypoints_str = "|".join(f"{lat},{lon}" for lat, lon in waypoints)
    url += f"&waypoints={waypoints_str}"
    
    return url, route_points

def calculate_similarity(gpx_points, google_points):
    # Convert to numpy arrays for easier computation
    gpx_array = np.array(gpx_points)
    google_array = np.array(google_points)
    
    # Use directed Hausdorff distance for similarity measure
    hausdorff_dist = max(directed_hausdorff(gpx_array, google_array)[0], directed_hausdorff(google_array, gpx_array)[0])
    return hausdorff_dist

def iteratively_optimize_route(gpx_points, api_key, iterations=200, mode="bicycling"):
    best_url, best_google_points = generate_google_maps_route(api_key, gpx_points, mode)
    best_similarity = calculate_similarity(gpx_points, best_google_points)
    best_sampled_waypoints = gpx_points
    
    for _ in range(iterations):
        print(_)
        # Randomly sample the waypoints and regenerate the Google Maps route
        if len(gpx_points) > 23:
            sampled_waypoints = random.sample(gpx_points[:-1], 21)  # Randomly sample waypoints
            sampled_waypoints = [gpx_points[0]] + sampled_waypoints + [gpx_points[-1]]
        else:
            sampled_waypoints = gpx_points
        url, google_points = generate_google_maps_route(api_key, sampled_waypoints, mode)
        similarity = calculate_similarity(gpx_points, google_points)
        
        if similarity < best_similarity:
            best_url, best_google_points = url, google_points
            best_similarity = similarity
            best_sampled_waypoints = sampled_waypoints
    
    return best_url, best_similarity, best_sampled_waypoints, best_google_points

def create_map(original_waypoints, sampled_waypoints, google_points, map_output_path='map.html'):
    # Create a map centered around the first waypoint
    start_location = original_waypoints[0]
    m = folium.Map(location=start_location, zoom_start=13)

    # Add original GPX route as a polyline
    folium.PolyLine(original_waypoints, color="blue", weight=2.5, opacity=1, popup='Original GPX Route').add_to(m)

    # Add sampled waypoints as a polyline
    folium.PolyLine(sampled_waypoints, color="green", weight=2.5, opacity=1, popup='Sampled Waypoints').add_to(m)

    # Add Google Maps route as a polyline
    folium.PolyLine(google_points, color="red", weight=2.5, opacity=1, popup='Google Maps Route').add_to(m)

    # Save the map to an HTML file
    m.save(map_output_path)
    print(f"Map saved to {map_output_path}")

def main(gpx_file_path, api_key):
    gpx_points = parse_gpx(gpx_file_path)
    url, similarity, best_sampled_waypoints, best_google_points = iteratively_optimize_route(gpx_points, api_key)
    print(f"Optimized Google Maps Route URL: {url}")
    print(f"Similarity to original GPX trace (Hausdorff distance): {similarity} meters")
    
    create_map(gpx_points, best_sampled_waypoints, best_google_points)

if __name__ == "__main__":
    # Path to your GPX file
    gpx_file_path = "valleedechevreuse.gpx"
    # Your Google Maps API key (ensure to keep it secure)
    api_key = "xxxxxxxxxxxxxxxxxxxxxx"  # Ensure you have set this environment variable
    
    main(gpx_file_path, api_key)
