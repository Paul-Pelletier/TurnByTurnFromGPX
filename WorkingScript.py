import gpxpy
import gpxpy.gpx
import googlemaps
import os
import numpy as np
from geopy.distance import geodesic
from sklearn.metrics import mean_squared_error
import random
import folium

def parse_gpx(file_path):
    print(f"Parsing GPX file: {file_path}")
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    waypoints = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                waypoints.append((point.latitude, point.longitude))
    print(f"Found {len(waypoints)} waypoints in GPX file.")
    return waypoints

def generate_google_maps_route(api_key, waypoints, mode="bicycling"):
    print("Generating Google Maps route...")
    gmaps = googlemaps.Client(key=api_key)
    
    max_waypoints = 20  # Adjusted to 20 waypoints plus start and end points
    if len(waypoints) > max_waypoints + 2:
        waypoints = sample_waypoints(waypoints, max_waypoints + 2)
    
    origin = waypoints[0]
    destination = waypoints[-1]
    waypoints = waypoints[1:-1]

    # Make sure waypoints are formatted as GPS coordinates
    waypoints = [f"{lat},{lon}" for lat, lon in waypoints]

    result = gmaps.directions(
        origin,
        destination,
        mode=mode,
        waypoints=waypoints,
        optimize_waypoints=True
    )

    if not result:
        raise ValueError("No route found.")

    route_points = []
    for leg in result[0]['legs']:
        for step in leg['steps']:
            start_location = step['start_location']
            route_points.append((start_location['lat'], start_location['lng']))
            end_location = step['end_location']
            route_points.append((end_location['lat'], end_location['lng']))
    
    url = f"https://www.google.com/maps/dir/{origin[0]},{origin[1]}"
    for waypoint in waypoints:
        url += f"/{waypoint}"
    url += f"/{destination[0]},{destination[1]}"
    
    print(f"Generated Google Maps route URL: {url}")
    return url, route_points

def sample_waypoints(waypoints, max_waypoints):
    interval = len(waypoints) // (max_waypoints - 1)
    sampled_waypoints = waypoints[::interval]
    if len(sampled_waypoints) > max_waypoints:
        sampled_waypoints = sampled_waypoints[:max_waypoints]
    if waypoints[-1] not in sampled_waypoints:
        sampled_waypoints.append(waypoints[-1])
    return sampled_waypoints

def calculate_mse(gpx_points, google_points):
    print("Calculating MSE between GPX points and Google Maps points...")
    
    gpx_array = np.array(gpx_points)
    google_array = np.array(google_points)
    
    lat_interpolated = np.interp(np.linspace(0, 1, len(gpx_array)), np.linspace(0, 1, len(google_array)), google_array[:, 0])
    lon_interpolated = np.interp(np.linspace(0, 1, len(gpx_array)), np.linspace(0, 1, len(google_array)), google_array[:, 1])
    interpolated_google = np.vstack((lat_interpolated, lon_interpolated)).T
    
    mse = mean_squared_error(gpx_array, interpolated_google)
    print(f"Calculated MSE: {mse}")
    return mse

def calculate_total_distance(points):
    total_distance = 0.0
    for i in range(len(points) - 1):
        total_distance += geodesic(points[i], points[i + 1]).kilometers
    return total_distance

def iteratively_optimize_route(gpx_points, api_key, iterations=10, mode="bicycling"):
    print("Starting iterative optimization of route...")
    best_url, best_google_points = generate_google_maps_route(api_key, gpx_points, mode)
    best_similarity = calculate_mse(gpx_points, best_google_points)
    best_sampled_waypoints = gpx_points
    
    for iteration in range(iterations):
        print(f"Iteration {iteration + 1} of {iterations}...")
        if len(gpx_points) > 20:
            sampled_waypoints = sample_waypoints(gpx_points, 20)
        else:
            sampled_waypoints = gpx_points
        url, google_points = generate_google_maps_route(api_key, sampled_waypoints, mode)
        similarity = calculate_mse(gpx_points, google_points)
        
        if similarity < best_similarity:
            print("Found better similarity. Updating best route...")
            best_url, best_google_points = url, google_points
            best_similarity = similarity
            best_sampled_waypoints = sampled_waypoints
    
    print("Optimization complete.")
    return best_url, best_similarity, best_sampled_waypoints, best_google_points

def create_map(original_waypoints, sampled_waypoints, google_points, map_output_path='map.html'):
    print(f"Creating map and saving to {map_output_path}...")
    start_location = original_waypoints[0]
    m = folium.Map(location=start_location, zoom_start=13)

    folium.PolyLine(original_waypoints, color="blue", weight=2.5, opacity=1, popup='Original GPX Route').add_to(m)
    folium.PolyLine(sampled_waypoints, color="green", weight=2.5, opacity=1, popup='Sampled Waypoints').add_to(m)
    folium.PolyLine(google_points, color="red", weight=2.5, opacity=1, popup='Google Maps Route').add_to(m)

    m.save(map_output_path)
    print(f"Map saved to {map_output_path}")

def main(gpx_file_path, api_key):
    print("Starting main process...")
    gpx_points = parse_gpx(gpx_file_path)
    url, similarity, best_sampled_waypoints, best_google_points = iteratively_optimize_route(gpx_points, api_key)
    print(f"Optimized Google Maps Route URL: {url}")
    print(f"Similarity to original GPX trace (MSE): {similarity}")
    
    original_distance = calculate_total_distance(gpx_points)
    google_distance = calculate_total_distance(best_google_points)
    print(f"Total distance of the initial GPX trace: {original_distance:.2f} km")
    print(f"Total distance of the Google Maps trace: {google_distance:.2f} km")
    
    create_map(gpx_points, best_sampled_waypoints, best_google_points)
    print("Main process complete.")
    return url

if __name__ == "__main__":
    
    # Path to your GPX file
    gpx_file_path = "valleedechevreuse.gpx"
    # Your Google Maps API key (ensure to keep it secure)
    api_key = "xxxxxxxxxxxx"  # Ensure you have set this environment variable
    
    main(gpx_file_path, api_key)
