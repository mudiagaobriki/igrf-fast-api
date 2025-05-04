import requests
import json

# The input format specified in the issue description
data = {
    "points_json": [
        {
            "altitude": "253.74992",
            "declination": "-0.2038665538950541",
            "horizontal intensity": "29930.97484076312",
            "inclination": "6.459262061307878",
            "latitude": "13.9375",
            "longitude": "4.0625",
            "total intensity": "-106.4984519265427",
            "vertical intensity": "29930.785372223898",
            "year": "2024.9"
        }
    ]
}

# Convert the data to JSON
json_data = json.dumps(data)

# Send a POST request to the /pyigrf endpoint
response = requests.post("http://localhost:8000/pyigrf", data=json_data, headers={"Content-Type": "application/json"})

# Print the response
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")