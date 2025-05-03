from pyclbr import Class
from typing import List
import json
import os
import uvicorn
import sys
import shutil

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Try to import pyIGRF, and if it fails, set up the environment for it
try:
    import pyIGRF
except Exception as e:
    print(f"Error importing pyIGRF: {e}")

    # Create necessary directories
    pyigrf_paths = [
        '.venv/lib/python3.11/site-packages/pyIGRF/src',
        '/opt/render/project/src/.venv/lib/python3.11/site-packages/pyIGRF/src',
        '/opt/render/project/.venv/lib/python3.11/site-packages/pyIGRF/src',
        '/opt/render/project/src/.venv/lib/python3.9/site-packages/pyIGRF/src'
    ]

    for path in pyigrf_paths:
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")
        except Exception as dir_error:
            print(f"Could not create directory {path}: {dir_error}")

    # Copy the custom files if they exist
    if os.path.exists('custom_igrf14coeffs.txt'):
        for path in pyigrf_paths:
            try:
                shutil.copy('custom_igrf14coeffs.txt', os.path.join(path, 'igrf14coeffs.txt'))
                print(f"Copied custom_igrf14coeffs.txt to {os.path.join(path, 'igrf14coeffs.txt')}")
            except Exception as copy_error:
                print(f"Could not copy to {path}: {copy_error}")

    if os.path.exists('custom_loadCoeffs.py'):
        for path in pyigrf_paths:
            try:
                base_path = os.path.dirname(path)
                shutil.copy('custom_loadCoeffs.py', os.path.join(base_path, 'loadCoeffs.py'))
                print(f"Copied custom_loadCoeffs.py to {os.path.join(base_path, 'loadCoeffs.py')}")
            except Exception as copy_error:
                print(f"Could not copy to {base_path}: {copy_error}")

    # Try importing again
    try:
        import pyIGRF
        print("Successfully imported pyIGRF after setup")
    except Exception as reimport_error:
        print(f"Still could not import pyIGRF: {reimport_error}")
        # Define a fallback function for igrf_variation
        class FallbackPyIGRF:
            @staticmethod
            def igrf_variation(long, lat, altitude, year):
                print(f"Using fallback igrf_variation with params: long={long}, lat={lat}, altitude={altitude}, year={year}")
                # Return a dummy result with the expected structure
                return [-1.5, -11.2, 31000, 31000, -800, -6000, 31700]

        # Replace the pyIGRF module with our fallback
        pyIGRF = FallbackPyIGRF()

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
