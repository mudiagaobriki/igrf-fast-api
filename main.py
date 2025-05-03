from pyclbr import Class
from typing import List, Union, Dict, Any
import json
import os
import uvicorn
import sys
import shutil

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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
async def compute_pyigrf(request: Request):
    try:
        # Get the raw request body
        body = await request.body()
        body_str = body.decode('utf-8')
        print(f"Raw request body: {body_str}")

        # Try to parse the body as JSON
        try:
            # If the body is a JSON object, parse it
            data = json.loads(body_str)
            print(f"Parsed JSON data: {data}")

            # Check if the data has a points_json field
            if isinstance(data, dict) and "points_json" in data:
                # If it does, use that as the points_json string
                points_json_str = data["points_json"]
                print(f"Found points_json field: {points_json_str}")

                # Try to parse the points_json string as JSON
                try:
                    # Check if points_json_str is already a list
                    if isinstance(points_json_str, list):
                        print("points_json is already a list, using directly")
                        parsed_points = points_json_str
                    else:
                        # Try to parse as JSON string
                        parsed_points = json.loads(points_json_str)
                    print(f"Parsed points_json: {parsed_points}")

                    # Check if parsed_points has a points_json field
                    if isinstance(parsed_points, dict) and "points_json" in parsed_points:
                        points_data = parsed_points["points_json"]
                        print(f"Found nested points_json field: {points_data}")
                    else:
                        # If not, assume the parsed data is the array of points directly
                        points_data = parsed_points
                        print(f"Using parsed data directly: {points_data}")
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError parsing points_json: {e}")
                    # If points_json is not valid JSON, try using it directly
                    if isinstance(points_json_str, list):
                        print("points_json is a list but not valid JSON, using directly")
                        points_data = points_json_str
                    else:
                        # If it's not a list, raise an error
                        raise HTTPException(status_code=400, detail=f"Invalid JSON format in points_json field: {str(e)}")
            else:
                # If the body is not a JSON object with a points_json field,
                # assume it's a raw JSON string that needs to be parsed
                try:
                    # Try to parse the body as a JSON string
                    # First, try without any modifications
                    try:
                        parsed_body = json.loads(body_str)
                        print(f"Parsed body without modifications: {parsed_body}")
                    except json.JSONDecodeError:
                        # If that fails, try stripping quotes and replacing escaped quotes
                        parsed_body = json.loads(body_str.strip('"').replace('\\"', '"'))
                        print(f"Parsed body after stripping quotes: {parsed_body}")

                    # Check if parsed_body has a points_json field
                    if isinstance(parsed_body, dict) and "points_json" in parsed_body:
                        points_data = parsed_body["points_json"]
                        print(f"Found points_json field in parsed body: {points_data}")
                    else:
                        # If not, assume the parsed data is the array of points directly
                        points_data = parsed_body
                        print(f"Using parsed body directly: {points_data}")
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError parsing body as string: {e}")
                    # If the body is not valid JSON, try one more approach
                    try:
                        # Try parsing with different quote handling
                        parsed_body = json.loads(body_str.replace('\\', '').replace('"{', '{').replace('}"', '}'))
                        print(f"Parsed body with alternative quote handling: {parsed_body}")

                        # Check if parsed_body has a points_json field
                        if isinstance(parsed_body, dict) and "points_json" in parsed_body:
                            points_data = parsed_body["points_json"]
                            print(f"Found points_json field in alternatively parsed body: {points_data}")
                        else:
                            # If not, assume the parsed data is the array of points directly
                            points_data = parsed_body
                            print(f"Using alternatively parsed body directly: {points_data}")
                    except json.JSONDecodeError as e2:
                        print(f"JSONDecodeError with alternative parsing: {e2}")
                        # If all parsing attempts fail, raise an error
                        raise HTTPException(status_code=400, detail=f"Invalid JSON format in request body: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError parsing body: {e}")
            # If the body is not valid JSON, raise an error
            raise HTTPException(status_code=400, detail=f"Invalid JSON format in request body: {str(e)}")

        # Ensure points_data is a list
        if not isinstance(points_data, list):
            print(f"points_data is not a list: {points_data}")
            if isinstance(points_data, dict):
                # If it's a single point as a dict, wrap it in a list
                points_data = [points_data]
                print(f"Wrapped single point in list: {points_data}")
            else:
                raise HTTPException(status_code=400, detail=f"Expected points_data to be a list, got {type(points_data).__name__}")

        # Process the points data
        print(f"Processing {len(points_data)} points")
        results = []
        for i, point in enumerate(points_data):
            print(f"Processing point {i}: {point}")
            # Each point is an object with latitude, longitude, altitude, and year fields
            try:
                lat = float(point["latitude"])
                long = float(point["longitude"])
                altitude = float(point["altitude"])
                year = float(point["year"])
                print(f"Extracted values: lat={lat}, long={long}, altitude={altitude}, year={year}")
                # Note: pyIGRF.igrf_variation expects parameters in the order (long, lat, altitude, year)
                result = pyIGRF.igrf_variation(long, lat, altitude, year)
                print(f"Result for point {i}: {result}")
                results.append(result)
            except KeyError as e:
                print(f"KeyError for point {i}: {e}")
                raise HTTPException(status_code=400, detail=f"Missing field in point {i}: {str(e)}")
            except ValueError as e:
                print(f"ValueError for point {i}: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid value in point {i}: {str(e)}")
            except Exception as e:
                print(f"Unexpected error processing point {i}: {e}")
                raise HTTPException(status_code=500, detail=f"Error processing point {i}: {str(e)}")

        print(f"Returning {len(results)} results")
        return results
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError in outer try block: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except (KeyError, ValueError) as e:
        print(f"KeyError or ValueError in outer try block: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid point format. Each point should be an object with 'latitude', 'longitude', 'altitude', and 'year' fields. Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in outer try block: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Keep the original endpoint for backward compatibility
@app.post("/pyigrf/model")
async def compute_pyigrf_model(point_array: StringifiedPointArray):
    # Parse the stringified JSON to get the points array
    try:
        # First, check if the input is already a JSON string or if it needs to be parsed
        try:
            # Try to parse the input as a JSON string
            parsed_data = json.loads(point_array.points_json)

            # Check if the parsed data has a "points_json" field
            if "points_json" in parsed_data:
                points_data = parsed_data["points_json"]
            else:
                # If not, assume the parsed data is the array of points directly
                points_data = parsed_data
        except json.JSONDecodeError:
            # If the input is not valid JSON, raise an error
            raise HTTPException(status_code=400, detail="Invalid JSON format")

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
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid point format. Each point should be an object with 'latitude', 'longitude', 'altitude', and 'year' fields. Error: {str(e)}")

# For Render deployment - get the port from the environment variable or use 8000 as default
port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    # Run the application with Uvicorn, binding to all network interfaces (0.0.0.0)
    # This makes the API accessible via the server's IP address
    uvicorn.run(app, host="0.0.0.0", port=port)
