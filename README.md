GPX to Google Maps Directions Optimizer

This project provides a solution to optimize Google Maps routes from GPX files, aiming to match the original GPX track as closely as possible. The script samples waypoints from the GPX file, generates a Google Maps route, and iteratively improves the route to minimize the mean squared error (MSE) between the GPX track and the Google Maps route.

Features
Parse GPX files to extract waypoints.
Generate Google Maps routes with up to 20 waypoints.
Optimize Google Maps routes to closely match the original GPX track using mean squared error.
Visualize the GPX track, sampled waypoints, and the optimized Google Maps route on an interactive map.

Requirements
Python 3.6+
gpxpy library
googlemaps library
numpy library
geopy library
scikit-learn library
folium library
