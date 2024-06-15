import googlemaps

api_key = "AIzaSyC3VFBy6bFcLuGpFa9eDzBtuy-gH2Bj_4E"
gmaps = googlemaps.Client(key=api_key)

try:
    result = gmaps.directions("New York, NY", "Los Angeles, CA")
    print(result)
except googlemaps.exceptions.ApiError as e:
    print("ApiError:", e)
except Exception as e:
    print("Error:", e)
