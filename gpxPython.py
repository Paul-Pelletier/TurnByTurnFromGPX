import gpxpy
import gpxpy.gpx
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

def create_map(waypoints, map_output_path='map.html'):
    # Create a map centered around the first waypoint
    start_location = waypoints[0]
    m = folium.Map(location=start_location, zoom_start=13)

    # Add GPX route as a polyline
    folium.PolyLine(waypoints, color="blue", weight=2.5, opacity=1).add_to(m)

    # Save the map to an HTML file
    m.save(map_output_path)
    print(f"Map saved to {map_output_path}")

def main(gpx_file_path):
    waypoints = parse_gpx(gpx_file_path)
    create_map(waypoints)

if __name__ == "__main__":
    # Path to your GPX file
    gpx_file_path = "valleedechevreuse.gpx"
    
    main(gpx_file_path)
