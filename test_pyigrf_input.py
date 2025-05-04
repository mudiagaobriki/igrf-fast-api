import requests
import json

# The input format specified in the issue description
data = [
    {"latitude":"13.9375","longitude":"4.0625","altitude":"253.74992","year":"2024.9"},
    {"latitude":"13.9375","longitude":"4.1875","altitude":"255.7499","year":"2024.9"},
    {"latitude":"13.8125","longitude":"4.0625","altitude":"301.00001","year":"2024.9"},
    {"latitude":"13.8125","longitude":"4.1875","altitude":"307.25054","year":"2024.9"},
    {"latitude":"13.9375","longitude":"4.3125","altitude":"275.74988","year":"2024.9"}
]

# Convert the data to JSON
json_data = json.dumps(data)

# Send a POST request to the /pyigrf endpoint
response = requests.post("http://localhost:8000/pyigrf", data=json_data, headers={"Content-Type": "application/json"})

# Print the response
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")