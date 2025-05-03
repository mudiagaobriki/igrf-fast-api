import requests
import json

# The URL of the API
url = "http://localhost:8000/pyigrf"

# The request body
request_body = "{\"points_json\":[{\"latitude\":\"13.9375\",\"longitude\":\"4.0625\",\"altitude\":\"253.74992\",\"year\":\"2024.9\"},{\"latitude\":\"13.9375\",\"longitude\":\"4.1875\",\"altitude\":\"255.7499\",\"year\":\"2024.9\"},{\"latitude\":\"13.8125\",\"longitude\":\"4.0625\",\"altitude\":\"301.00001\",\"year\":\"2024.9\"},{\"latitude\":\"13.8125\",\"longitude\":\"4.1875\",\"altitude\":\"307.25054\",\"year\":\"2024.9\"},{\"latitude\":\"13.9375\",\"longitude\":\"4.3125\",\"altitude\":\"275.74988\",\"year\":\"2024.9\"}]}"

# Send the request
response = requests.post(url, data=request_body, headers={"Content-Type": "application/json"})

# Print the response
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    print("Response:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Error: {response.text}")