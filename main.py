from pyclbr import Class
from typing import List
import json
import os
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyIGRF

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class DataPoint(BaseModel):
    long: float
    lat: float
    altitude: float
    year: float

class PointArray(BaseModel):
    points: List[List[str]]

class StringifiedPointArray(BaseModel):
    points_json: str

points = {
    0: DataPoint(long=1234,lat=2468,altitude=500,year=2000),
}
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/points")
async def get_points():
    return points

@app.get("/points/{point_id}")
async def get_point(point_id: int)->DataPoint:
    if point_id not in points:
        raise HTTPException(status_code=404, detail="Not found")
    return points[point_id]

@app.get("/pyigrf/")
async def get_pyigrf():
    return pyIGRF.igrf_variation(100,100,500,2024.9)

@app.post("/pyigrf")
async def compute_pyigrf(point_array: StringifiedPointArray):
    # Parse the stringified JSON to get the points array
    try:
        parsed_data = json.loads(point_array.points_json)
        # The parsed data is already a JSON object with a "points_json" field
        points_data = parsed_data["points_json"]
        results = []
        for point in points_data:
            # Each point is an object with latitude, longitude, altitude, and year fields
            lat = float(point["latitude"])
            long = float(point["longitude"])
            altitude = float(point["altitude"])
            year = float(point["year"])
            # Note: pyIGRF.igrf_variation expects parameters in the order (long, lat, altitude, year)
            result = pyIGRF.igrf_variation(long, lat, altitude, year)
            results.append(result)
        return results
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid point format. Each point should be an object with 'latitude', 'longitude', 'altitude', and 'year' fields")

# For Render deployment - get the port from the environment variable or use 8000 as default
port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    # Run the application with Uvicorn, binding to all network interfaces (0.0.0.0)
    # This makes the API accessible via the server's IP address
    uvicorn.run(app, host="0.0.0.0", port=port)
